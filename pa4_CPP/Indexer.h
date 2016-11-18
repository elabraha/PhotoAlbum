#ifndef INDEXER_H
#define INDEXER_H

#include <iosfwd>
#include <set>
#include <string>
#include <vector>
#include <map>

class Indexer {
public:
    void index(std::ifstream& content, std::ostream& outfile);

private:
	std::set<std::string> stops;

	std::map<std::string, std::set<int>> inverted_index_table;

	std::vector<std::map<std::string, double>> words_in_doc;

	// Creates a structure to hold stop words
	void make_stops_object();

	void print_stops_object();

	void parse_caption(std::string caption, int doc_id);

	double calculate_normalization(std::map<std::string, double>& words, double N);

	double calculate_idf(double N, double n_k);

	std::string remove_non_alnum(std::string s);

	int calculate_total_occurrences(std::string key, std::set<int>& v);

	void print_inverted_index(std::ostream& file);

};

#endif
