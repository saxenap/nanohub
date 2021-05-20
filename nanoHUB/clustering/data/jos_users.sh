#!/bin/bash

ssh saxenap@db2.nanohub.org "mysql --batch  -e 'select id, name, email from nanohub.jos_users LIMIT 100;'" > test