#include <stdio.h>
#include <sqlite3.h>
#include <stdlib.h>
#include <string>
#include <iostream>
#include <curl/curl.h>

using namespace std;

string* json_buffer;

size_t write_data(char* data, size_t size, size_t nmemb, string* buffer) {
	json_buffer->append(data);
	return size * nmemb;
}

string get_JSON(string URL) {
	CURL* handle;
	CURLcode res;
	struct curl_slist* headers = NULL;
	headers = curl_slist_append(headers, "Accept: application/json");  
	headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "charset: utf-8");
    handle = curl_easy_init();

    if (handle) {
    	curl_easy_setopt(handle, CURLOPT_HTTPHEADER, headers);
    	curl_easy_setopt(handle, CURLOPT_URL, URL.c_str());
    	curl_easy_setopt(handle, CURLOPT_HTTPGET, 1);
    	curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_data);
    	curl_easy_setopt(handle, CURLOPT_WRITEDATA, json_buffer);
    	res = curl_easy_perform(handle);
    	cout << res << "\n";

    	if (CURLE_OK == res) {
    		char* ct;
    		res = curl_easy_getinfo(handle, CURLINFO_CONTENT_TYPE, &ct);
    		if (res == CURLE_OK && ct) {		
			    curl_slist_free_all(headers);
			    curl_easy_cleanup(handle);
			    return *json_buffer;
    		}
    	}
    }    
    curl_slist_free_all(headers);
    curl_easy_cleanup(handle);
    return "ERROR";
}

static int callback(void* NotUsed, int numCol, char** entries, char** colNames) {
	for (int i = 0; i < numCol; i++) {
		cout << colNames[i] << ": " << entries[i] << '\n';
	}
	return 0;
}

int main() {
	string buffer_content = "";
	json_buffer = &buffer_content;
	string a = get_JSON("https://nhentai.net/api/galleries/search?query=parody:blue+archive");
	cout << a;
	/*
	sqlite3* db;
	char* zErrMsg = NULL;
	int rc = sqlite3_open("test.db", &db);
	if (rc) {
		fprintf(stderr, "Can't open database %s\n", sqlite3_errmsg(db));
		return 0;
	}
	else {
		fprintf(stdout, "Opened database successfully.\n");
	}

	string sql = "INSERT INTO Test (name, car, style) VALUES('Centauri', 'Honda', 'DD');"
				 "INSERT INTO Test (name, car, style) VALUES('Xor', 'Hyundai', 'DD')";

	rc = sqlite3_exec(db, sql.c_str(), callback, 0, &zErrMsg);

	if (rc != SQLITE_OK) {
		fprintf(stderr, "SQL error: %s\n", zErrMsg);
		sqlite3_free(zErrMsg);
	}
	else {
		fprintf(stdout, "SQL executed successfully");
	}
	sqlite3_close(db);
	*/
	return 0;
}