rm -r chunks
rm -r intermediate
rm -r output
rm -r shuffled
split -n l/10 --numeric-suffixes --additional-suffix=.txt data.txt chunk
mkdir chunks
mv chunk* chunks/
mkdir intermediate
mkdir output
mkdir shuffled
rm final_result.txt