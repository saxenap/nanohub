<?php

class SshConfig
{
    public $username;
    public $password;
    public $hostname;
    public $port;

    public function __construct(
        string $username, string $password, string $hostname, int $port
    )
    {
        $this->username = $username;
        $this->password = $password;
        $this->hostname = $hostname;
        $this->port = $port;
    }
}

class MysqlConfig {
    public $username;
    public $password;
    public $hostname;
    public $port;

    public function __construct(
        string $username, string $password, string $hostname, int $port
    )
    {
        $this->username = $username;
        $this->password = $password;
        $this->hostname = $hostname;
        $this->port = $port;
    }
}

class SshTunneledDb2Connection
{
    public $ssh_config;
    public $mysql_config;

    public function __construct(SshConfig $ssh_config, MysqlConfig $mysql_config)
    {
        $this->ssh_config = $ssh_config;
        $this->mysql_config = $mysql_config;
    }

    public function query(string $query)
    {
        $connection = ssh2_connect($this->ssh_config->hostname, $this->ssh_config->port);
        if($connection === FALSE){
            throw new RuntimeException("Failed to connect with SSH server.");
        }

        if(!ssh2_auth_password($connection, $this->ssh_config->username, $this->ssh_config->password)){
              throw new RuntimeException("Failed to authenticate to SSH server");
        }

        $ssh_query ='ssh -L 3307:' . $this->ssh_config->hostname.':' .$this->mysql_config->port.';
        echo "' . str_replace( '"', '\'', stripslashes( $query ) ) . '" | mysql -u '.$this->mysql_config->username.' -h '.$this->mysql_config->hostname.' --password='.$this->mysql_config->password;

        $response = ssh2_exec($connection, $ssh_query);

        $error = ssh2_fetch_stream($response, SSH2_STREAM_STDERR);
        $error_response = stream_get_contents($error);
        //if(!is_null($error_response))
        //    throw new RuntimeException(sprintf("Error: %s", $error_response));

        stream_set_blocking($response, true);
        stream_set_blocking($error, true);

        return stream_get_contents($response);
    }
}

class SshTunneledConnectionFactory
{
    static public function create_from_environment()
    {
        $ssh_config = new SshConfig(
            getenv('tunnel_ssh_username'),
            getenv('tunnel_ssh_password'),
            getenv('tunnel_ssh_host'),
            getenv('tunnel_ssh_port')
        );

        $mysql_config = new MysqlConfig(
            getenv('db_user'),
            getenv('db_password'),
            getenv('db_host'),
            getenv('tunnel_remote_bind_port')
        );

        return new SshTunneledDb2Connection($ssh_config, $mysql_config);
    }
}