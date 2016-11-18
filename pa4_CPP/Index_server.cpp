#include "Index_server.h"

#include <cassert>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <pthread.h>
#include <sstream>
#include <cmath>
#include <set>
#include <map>
#include <algorithm>

#include "mongoose.h"

using std::cerr;
using std::cout;
using std::endl;
using std::ifstream;
using std::ostream;
using std::ostringstream;
using std::istringstream;
using std::string;
using std::vector;
using std::string;
using std::stoi;
using std::set;
using std::map;
using std::to_string;

// Port 6273

const string stops_filename = "stops.txt";

namespace {
    int handle_request(mg_connection *);
    int get_param(const mg_request_info *, const char *, string&);
    string get_param(const mg_request_info *, const char *);
    string to_json(const vector<Query_hit>&);

    ostream& operator<< (ostream&, const Query_hit&);
}

pthread_mutex_t mutex;

// Runs the index server on the supplied port number.
void Index_server::run(int port)
{
    // List of options. Last element must be NULL
    ostringstream port_os;
    port_os << port;
    string ps = port_os.str();
    const char *options[] = {"listening_ports",ps.c_str(),0};

    // Prepare callback structure. We have only one callback, the rest are NULL.
    mg_callbacks callbacks;
    memset(&callbacks, 0, sizeof(callbacks));
    callbacks.begin_request = handle_request;

    // Initialize the global mutex lock that effectively makes this server
    // single-threaded.
    pthread_mutex_init(&mutex, 0);

    // Start the web server
    mg_context *ctx = mg_start(&callbacks, this, options);
    if (!ctx) {
        cerr << "Error starting server." << endl;
        return;
    }

    pthread_exit(0);
}

// Load index data from the file of the given name.
void Index_server::init(ifstream& infile)
{
    // Fill in this method to load the inverted index from disk.
    string entry;
    while (getline(infile, entry)){
        parse_entry(entry);
    }

}

// Construct a inverted index table entry to add to inverted_index_table
void Index_server::parse_entry(string& str){
    istringstream s(str);

    string word, num;

    // Read word, IDF, and total occurrences from file
    s >> word;
    s >> num;
    inverted_index_table[word].IDF = stod(num);
    s >> num;
    inverted_index_table[word].total_occurrences = stoi(num);

    // Read document information from file
    while (s >> num){
        doc document;
        document.doc_id = stoi(num);
        s >> num;
        document.num_occurrences = stoi(num);
        s >> num;
        document.norm_factor = stod(num);
        inverted_index_table[word].docs.push_back(document);
    }

}

// Print inverted index table object - For debugging
void Index_server::print_inverted_index(){
    for (auto it = inverted_index_table.begin(); it != inverted_index_table.end(); it++){
        cout << it->first << " " << it->second.IDF << " " << it->second.total_occurrences << " ";
        for (auto it2 = it->second.docs.begin(); it2 != it->second.docs.end(); it2++){
            cout << it2->doc_id << " " << it2->num_occurrences << " " << it2->norm_factor << " ";
        } cout << endl;
    }
}

static double document_weight(double idf, double tf, double norm)
{
    return (tf*idf)/sqrt(norm);
}

bool sorter(Query_hit q1, Query_hit q2){
    return q1.score > q2.score;
}

// Used foe debugging
static void print_hits(vector<Query_hit> &v){
    cout << "Hit List:" << endl;
    for (auto it = v.begin(); it != v.end(); it++){
        cout << "(" << it->id << ", " << it->score << ")   " << endl;
    }
}

// Search the index for documents matching the query. The results are to be
// placed in the supplied "hits" vector, which is guaranteed to be empty when
// this method is called.
void Index_server::process_query(const string& query, vector<Query_hit>& hits)
{
    cout << "Processing query '" << query << "'" << endl;

    make_stops_object();

    istringstream s(query);
    string word;
    while (s >> word){
        transform(word.begin(), word.end(), word.begin(), ::tolower);
        word = remove_non_alnum(word);
        if (word.size() == 0) continue;
        if (stops.find(word) == stops.end()){
            if (query_map.find(word) == query_map.end()) query_map[word] = 1;
            else query_map[word]++;
        }
        
    }

    // Calculate the weights of the query terms

    double normalization = calculate_normalization(query_map);
    double w_query;
    double TF;
    double IDF;

    for (auto it = query_map.begin(); it != query_map.end(); it++){

        // If a quesry word is not in the inverted index table, return with hits == emptyset
        if (inverted_index_table.find(it->first) == inverted_index_table.end()) return;

        TF = it->second;
        IDF = inverted_index_table[it->first].IDF;
        w_query = (TF*IDF) / sqrt(normalization);
        query_weights[it->first] = w_query;
    }

    // for (auto it = query_weights.begin(); it != query_weights.end(); it++){
    //     cout << it->first << " " << it->second << endl;
    // }

    set<int> doc_hits;
    document_intersection(doc_hits);

    // cout << "doc_hits: " << doc_hits.size() << endl;
    // for (auto it = doc_hits.begin(); it != doc_hits.end(); it++){
    //     cout << *it << endl;
    // }

    map<int, double> hit_map;
    for (auto it = query_weights.begin(); it != query_weights.end(); it++){
        for (int i = 0; i < inverted_index_table[it->first].docs.size(); i++){
            if (doc_hits.find(inverted_index_table[it->first].docs[i].doc_id) != doc_hits.end()){
                double weight = document_weight(inverted_index_table[it->first].IDF,
                                                inverted_index_table[it->first].docs[i].num_occurrences,
                                                inverted_index_table[it->first].docs[i].norm_factor);
                if (hit_map.find(inverted_index_table[it->first].docs[i].doc_id) == hit_map.end())
                    hit_map[inverted_index_table[it->first].docs[i].doc_id] = (weight * it->second);
                else
                    hit_map[inverted_index_table[it->first].docs[i].doc_id] += (weight * it->second);
            }
        }
    }

    query_weights.clear();

    for (auto it = hit_map.begin(); it != hit_map.end(); it++){
        string s = to_string(it->first + 1);
        char *c  = new char[s.size()];
        strcpy(c, s.c_str());
        Query_hit q(c, it->second);
        hits.push_back(q);
    }
    sort(hits.begin(), hits.end(), sorter);

    print_hits(hits);
    
}

void Index_server::make_stops_object(){
    ifstream stops_file;
    stops_file.open(stops_filename);
    if (!stops_file.is_open()) {
        cerr << "Error opening file: " << stops_filename << endl;
        return;
    }
    string s;
    while (!stops_file.eof()){
        stops_file >> s;
        stops.insert(s);
    }
}

string Index_server::remove_non_alnum(string s){
    for (int i = 0; i < s.size(); i++)
        if (!isalnum(s[i])) s.erase(i);
    return s;
}

double Index_server::calculate_normalization(map<string, int>& words){
    double norm = 0;
    for (auto it = words.begin(); it != words.end(); it++)
    {
        double IDF = inverted_index_table[it->first].IDF;
        double TF = (double) it->second;
        norm += TF*TF*IDF*IDF;
    }
    return norm;
}

void Index_server::document_intersection(set<int> &s){

    std::set<int> set_temp;

    auto it = query_map.begin();
    // cout << "first word: " << inverted_index_table[it->first].docs.size() << endl;
    for (int i = 0; i < inverted_index_table[it->first].docs.size(); i++){
        set_temp.insert(inverted_index_table[it->first].docs[i].doc_id);
    }
    it++;

    if (it == query_map.end()) s = set_temp;

    while(it != query_map.end()){
        std::set<int> temp;
        for (int i = 0; i < inverted_index_table[it->first].docs.size(); i++){
            temp.insert(inverted_index_table[it->first].docs[i].doc_id);
        }
        s.clear();
        set_intersection(set_temp.begin(), set_temp.end(), temp.begin(), temp.end(), 
                                std::inserter(s, s.begin()));
        set_temp = s; 
        it++;
    }

    query_map.clear();
}

namespace {
    int handle_request(mg_connection *conn)
    {
        const mg_request_info *request_info = mg_get_request_info(conn);

        if (!strcmp(request_info->request_method, "GET") && request_info->query_string) {
            // Make the processing of each server request mutually exclusive with
            // processing of other requests.

            // Retrieve the request form data here and use it to call search(). Then
            // pass the result of search() to to_json()... then pass the resulting string
            // to mg_printf.
            string query;
            if (get_param(request_info, "q", query) == -1) {
                // If the request doesn't have the "q" field, this is not an index
                // query, so ignore it.
                return 1;
            }

            vector<Query_hit> hits;
            Index_server *server = static_cast<Index_server *>(request_info->user_data);

            pthread_mutex_lock(&mutex);
            server->process_query(query, hits);
            pthread_mutex_unlock(&mutex);

            string response_data = to_json(hits);
            for (int i = 0; i < hits.size(); i++)
            {
                delete[] hits[i].id;
            }
            int response_size = response_data.length();

            // Send HTTP reply to the client.
            mg_printf(conn,
                      "HTTP/1.1 200 OK\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: %d\r\n"
                      "\r\n"
                      "%s", response_size, response_data.c_str());
        }

        // Returning non-zero tells mongoose that our function has replied to
        // the client, and mongoose should not send client any more data.
        return 1;
    }

    int get_param(const mg_request_info *request_info, const char *name, string& param)
    {
        const char *get_params = request_info->query_string;
        size_t params_size = strlen(get_params);

        // On the off chance that operator new isn't thread-safe.
        pthread_mutex_lock(&mutex);
        char *param_buf = new char[params_size + 1];
        pthread_mutex_unlock(&mutex);

        param_buf[params_size] = '\0';
        int param_length = mg_get_var(get_params, params_size, name, param_buf, params_size);
        if (param_length < 0) {
            return param_length;
        }

        // Probably not necessary, just a precaution.
        param = param_buf;
        delete[] param_buf;

        return 0;
    }

    // Converts the supplied query hit list into a JSON string.
    string to_json(const vector<Query_hit>& hits)
    {
        ostringstream os;
        os << "{\"hits\":[";
        vector<Query_hit>::const_iterator viter;
        for (viter = hits.begin(); viter != hits.end(); ++viter) {
            if (viter != hits.begin()) {
                os << ",";
            }

            os << *viter;
        }
        os << "]}";

        return os.str();
    }

    // Outputs the computed information for a query hit in a JSON format.
    ostream& operator<< (ostream& os, const Query_hit& hit)
    {
        os << "{" << "\"id\":\"";
        int id_size = strlen(hit.id);
        for (int i = 0; i < id_size; i++) {
            if (hit.id[i] == '"') {
                os << "\\";
            }
            os << hit.id[i];
        }
        return os << "\"," << "\"score\":" << hit.score << "}";
    }
}
