from src.automation.data_access_layer import unit_of_work


def get_workflows_by_status(status: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = list(uow.session.execute(
            'SELECT * FROM X_OWNER.workflows WHERE status = :status',
            dict(status=status)
        ))
    return [dict(r) for r in results]