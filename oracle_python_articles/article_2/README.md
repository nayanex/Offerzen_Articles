 along with some Python features such as encapsulating your queries in classes and methods according to business rules domains and making your code more flexible and reusable by concatenating python variables in your queries commands using the format method.


Let's suppose you work for a financial institution and you are given a task to create Financial Audit Reports for a certain quarter of the year or month. These reports would provide detailed information about macroeconomic variables, mortgage rates and so on.

This is an important task because in the end these reports are going to be evaluated by an Auditing company, like EY or PwC, in order to make sure that the financial records are a fair and accurate representation of the transactions your company claim to represent.

The business analysts in your team usually work on these reports, many of them are already savvy about SQL commands and perform them using the Oracle SQL Developer software. But they don't want spend infinite boring hours performing repetitive queries and populating the results on excel sheets, so they ask your help to automate this process. After all, we are in the 21st century already and life is too short to repeat themselves every month or quarter. Plus, sometimes little mistakes are made here and there... damn humans. 

So, basically they would provide you with the queries they usually perform to gather the report data and you would adapt them according to the variant parameters, for example, year, month, quarter. In the beginning you are going to need some meetings to understand the business logic behind all of it, but once you get it, it's piece of cake. 

*src/automation/data_transfer_object/controls.py*
```python
from dataclasses import dataclass
from typing import Generic, TypeVar


RequiredData = TypeVar("RequiredData")


@dataclass
class QueryResult:
    data: list
    query_cmd: str


@dataclass
class GeneralData(Generic[RequiredData]):
    source_per_request: dict
    calculation_requests: QueryResult


@dataclass
class CalcGeneralData(GeneralData[RequiredData]):
    economic_scenario_projections: list
    mortgage_rates: QueryResult
```



*src/automation/data_access_layer/base_queries.py*
```python
from src.automation.data_access_layer import unit_of_work
from src.automation.data_transfer_object.controls import QueryResult


class BaseQueries:
    def __init__(self, uow: unit_of_work.SqlAlchemyUnitOfWork):
        self.uow = uow

    def _run_query(self, query_cmd: str) -> QueryResult:
        with self.uow:
            data = list(map(dict, self.uow.session.execute(query_cmd)))
            return QueryResult(data, query_cmd)

    def get_calc_request_ids(self, month: int, year: int) -> QueryResult:
        query = """
SELECT R.ID 
FROM
    X_OWNER.CALCULATION_REQUESTS R,
    X_OWNER.CALCULATION_INPUTS I
WHERE
    R.M_IMPORT_DATASET_ID = I.IMPORT_DATASET_ID AND
    TO_CHAR(R.CREATION_TIMESTAMP, 'mm-YYYY') =  '{month}-{year}' AND
    R.DESCRIPTION IS NULL AND
    R.STATUS NOT IN ('FAILED')
        """.format(
            month=str(month).zfill(2), year=year
        )
        results = self._run_query(query)
        results.data = [str(r["id"]) for r in results.data]
        return results
```
