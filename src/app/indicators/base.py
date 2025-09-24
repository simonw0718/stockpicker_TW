from typing import Callable, Dict, Any, Optional, List, Union
import pandas as pd

IndicatorFn = Callable[[pd.DataFrame, Dict[str, Any]], Union[pd.Series, pd.DataFrame]]

class IndicatorMeta(dict):
    """timeframes / fields / default_field / warmup(params)->int"""
    pass
