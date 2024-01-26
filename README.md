# tak-walkers

1. Obtain the .p12 file for a user and the truststore-CA.p12
2. Convert the .p12's to PEM Files
  openssl pkcs12 -in user_cert.p12 -out client.pem -nodes -passin atakatak
  openssl pkcs12 -in truststore-CA.p12 -out server.pem -nodes -nokeys -passin atakatak

Server CN is the FQDN of the server cert that was created with the ./makeCert server command.
