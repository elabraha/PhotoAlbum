#include "Indexer.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <cmath>
#include <algorithm>

using namespace std;

const string stops_filename = "stops.txt";

// Reads content from the supplied input file stream, and transforms the
// content into the actual on-disk inverted index file.
void Indexer::index(ifstream& content, ostream& outfile)
{

	make_stops_object();

	string caption;
	int doc_id = 0;
	while (getline(content, caption)){
		parse_caption(caption, doc_id);
		doc_id++;
	}

	print_inverted_index(outfile);

}

// Makes a set of all the stop words
void Indexer::make_stops_object(){
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

// Used for debugging
void Indexer::print_stops_object(){
	for (auto it = stops.begin(); it != stops.end(); it++) cout << *it << endl;
}

// Put documents words into temporary document map
void Indexer::parse_caption(string caption, int doc_id){
	map<string, double> caption_map;
	istringstream s(caption);
	string word;
	while (s >> word){
		transform(word.begin(), word.end(), word.begin(), ::tolower);
		word = remove_non_alnum(word);
		if (stops.find(word) == stops.end()){		// if not a stop word
			if (word.size() == 0) continue;
			if (caption_map.find(word) == caption_map.end()) caption_map[word] = 1;
			else caption_map[word]++;
			inverted_index_table[word].insert(doc_id);
		}
	}
	words_in_doc.push_back(caption_map);
}

double Indexer::calculate_normalization(map<string, double>& words, double N){
	double norm = 0;
	for (auto it = words.begin(); it != words.end(); it++)
	{
		double n_k = (double)inverted_index_table[it->first].size();
		norm += (it->second*it->second) * (log10(N/n_k)*log10(N/n_k));
	}
	return norm;
}

double Indexer::calculate_idf(double N, double n_k){
	return log10(N/n_k);
}

string Indexer::remove_non_alnum(string s){
	for (int i = 0; i < s.size(); i++)
		if (!isalnum(s[i])) s.erase(i);
	return s;
}

int Indexer::calculate_total_occurrences(string key, set<int>& s){
	int total = 0;
	for (auto it = s.begin(); it != s.end(); it++){
		total += words_in_doc[*it][key];
	}
	return total;
}

void Indexer::print_inverted_index(ostream& file){
	for (auto it = inverted_index_table.begin(); it != inverted_index_table.end(); it++){
		file << it->first << " " << calculate_idf((double)words_in_doc.size(), (double)it->second.size());
		file << " " << calculate_total_occurrences(it->first, it->second);
		for (auto it2 = it->second.begin(); it2 != it->second.end(); it2++){
			file << " " << *it2 << " " << words_in_doc[*it2][it->first] << " ";
			file << calculate_normalization(words_in_doc[*it2], (double)words_in_doc.size());
		}
		file << endl;
	}
}

