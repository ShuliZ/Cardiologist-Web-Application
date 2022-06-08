import logging

import pandas as pd

logger = logging.getLogger(__name__)

def import_data(path: str) -> pd.DataFrame:
    """Read data from "path" into a DataFrame
    Args:
        path (`str`): file name path
    Returns:
        data (:obj:`DataFrame <pandas.DataFrame>`): heart disease DataFrame
    """

    try:
        data = pd.read_csv(path)
    # error when unable to find the input file
    except FileNotFoundError:
        logger.error('No such file or directory, please check the input file.')
        return pd.DataFrame()
    except pd.errors.ParserError:
        logger.error('The input file has incorrect format')
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        logger.error('The data frame is empty')
        return pd.DataFrame()
    else:
        logger.info('Input data loaded from %s', path)
        return data
