#include "Indexer.h"

#include <fstream>
#include <iostream>

using std::cerr;
using std::endl;
using std::ifstream;
using std::ofstream;

int main(int argc, char *argv[])
{
    if (argc < 3) {
        cerr << "Usage: indexer <content-filename> <inverted-index-filename>" << endl;
        return -1;
    }

    const char *content_fname = argv[1];
    ifstream content(content_fname);
    if (!content.is_open()) {
        cerr << "Error opening file: " << content_fname << endl;
        return -1;
    }

    const char *index_fname = argv[2];
    ofstream outfile(index_fname);
    if (!outfile.is_open()) {
        cerr << "Error opening file: " << index_fname << endl;
        return -1;
    }

    Indexer indexer;
    indexer.index(content, outfile);

    return 0;
}
