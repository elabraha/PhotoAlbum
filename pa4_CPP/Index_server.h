#ifndef INDEX_SERVER_H
#define INDEX_SERVER_H

#include <iosfwd>
#include <stdint.h>
#include <string>
#include <vector>
#include <map>
#include <set>

struct Query_hit {
    Query_hit(const char *id_, double score_)
        : id(id_), score(score_)
        {}

    const char *id;
    double score;
};

class Index_server {
public:
    void run(int port);

    // Methods that students must implement.
    void init(std::ifstream& infile);
    void process_query(const std::string& query, std::vector<Query_hit>& hits);

private:
	std::set<std::string> stops;

	struct doc {
		int doc_id;
		int num_occurrences;
		double norm_factor;
	};

	struct IIT_entry {
		double IDF;
		int total_occurrences;
		std::vector<doc> docs;
	};

	std::map<std::string, IIT_entry> inverted_index_table;

	std::map<std::string, int> query_map;

	std::map<std::string, double> query_weights;

	void make_stops_object();

	void parse_entry(std::string& str);

	void print_inverted_index();

	std::string remove_non_alnum(std::string s);

	double calculate_normalization(std::map<std::string, int>& words);

	void document_intersection(std::set<int> &set);

};

#endif
