from nanoHUB.containers import Container
from nanoHUB.settings import Settings


def main() -> None:
    print("Main called")

    db_connection = container.db_connection_factory()
    print(db_connection)

if __name__ == '__main__':
    # print(os.environ['db_host'])
    container = Container()
    container.config.from_pydantic(Settings())
    assert container.config.salesforce.client_id() == '3MVG95jctIhbyCppj0SNJ75IsZ1y8UPGZtSNF4j8FNVXz.De8Lu4jHm3rjRosAtsHy6qjHx3i4S_QbQzvBePG'
    assert container.config.database.password() == 'P6MBk407A4PNDEwE'

    main()
