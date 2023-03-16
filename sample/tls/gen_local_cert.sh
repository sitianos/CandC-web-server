# generate private key of local CA
openssl genrsa -out localCA.key 2048

# generate CSR and certification of private CA
openssl req -out localCA.csr -key localCA.key -new
openssl x509 -req -days 3650 -signkey localCA.key -in localCA.csr -out localCA.crt

# generate private key of localhost server
openssl genrsa -out localhost.key 2048

openssl req -out localhost.csr -key localhost.key -new

# make SAN extention file
echo 'subjectAltName = DNS:localhost, IP:127.0.0.1' > localhost.csx

# issue certification of localhost server
openssl x509 -req -days 1825 -CA localCA.crt -CAkey localCA.key -CAcreateserial -in localhost.csr -extfile localhost.csx -out localhost.crt
