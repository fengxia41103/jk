Using Ubuntu 18.04 as host.

# Docker

1. Copy `static` files to `../static` &larr; if you have a different
   location, check `docker-compose` for service `web` to see where it
   is expecting to bind this volume, and if you know docker, you can
   change the `source` path (either relative or absolute).
   
2. `docker-compose up`. If you want to bring them up one by one,
   sequence will be `db`, `redis`, then `web`.

# Setup MySQL

1. Instally mysql: `apt install mysql-server`
2. Edit `/etc/mysql/mysql.conf.d/mysqld.cnf`, set `bind-address =
   <host ip>`, then `systemctl restart mysql`.
3. By default, no password is set. `sudo mysql -u root` on mysql host
   to get `mysql>`.
4. Select db: `use mysql`
5. Use password as authentication: `UPDATE user SET plugin="mysql_native_password" WHERE User='root';`
4. Change pwd: `ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';`
5. Grant options: `GRANT ALL ON *.* TO 'root'@'localhost';`
6. `flush privileges;`
7. On a terminal on the mysql host, `mysql -u root -p`,
   using the pwd set in step 5, you should succeed. 

However, if you connect from another host remotely to this MySQL, it
will fail. 
