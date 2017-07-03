# Hashtag analysis through the specialized combination of word embeddings

### Kenneth Sanders

## Installation

  
//TODO full explanation on how to run the program.
   ###Requires
   Python 2.7
   Python libraries: nltk, matplotlib, tensorflow, psycopg2, pyclustering, scipy, sklearn, and argparse.
   PSQL database filled with public schema and data already in the respective tables (see Library/Database.py for more info.)
   
//TODO check for more requirements
//TODO add links to installation for all requirements

   ###Database setup
   //TODO give columns needed in each table
   Change the database information found in Library/Database.py so that the program can connect to the PSQL database.

## Running

   Ensure that the tweets, hashtags, and tweets_hashtags table are in the public schema, and that the psql login info has all permissions on the whole database (all may not be necessary, but the program definitely needs to be able to create schemas and tables, truncate tables, and select and insert on all tables that are relevent).

   Run Data_Processing_Scripts/FormatTweets.py (no arguements should be needed) to do a one-time formatting (tokenization and stemming) of all tweet data and have it placed in the public.formatted_tweets table.

   Modify Data_Processing_Scripts/RunSpecific.py or RunDefault.py to suit the datasets you plan on using, and run the modified file.

## Abstract

## Project Structure
#### Folders
      *Library
          *Contains a collection of files with python functions for each step in the proceedure.
      *Data_Processing_Scripts
          *A collection of runnable scripts that are capable of parsing command line arguments and running the respective function(s) in the Library folder.
      *Results_Analysis
          *Folder containing results analysis scripts to allow easy analysis of the resulting embeddings.




