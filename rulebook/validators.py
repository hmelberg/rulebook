

def del_row(df, col=None, ok=None):
   df = df[ok]
   return df


def to_nan(df, col=None, ok=None):
   df.loc[~ ok, col] = np.nan
   return df


def insert(df, col, value):
   df.loc[~ok, col] = value
   return df


def not_contains(df, col, text):
   not_ok = df.str.contains(text, na=False)
   ok = ~ not_ok
   return ok


def contains(df, col, text, case=True, flags=int, na=True, regex=True):
   ok = df.str.contains(text, case=case, flags=falgs, na=na, regex=regex)  # note na true, discuss!
   return ok


def replace(df, col, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
   df[col] = df[col].replace(to_replace=to_replace, value=value, inplace=inplace, limit=limit, regex=regex,
                             method=method)  # note na true, discuss!
   return df


def is_dtype(df, col, value='datetime'):
   ok = (df.col.dtype == value)
   return ok


def to_dtype(df, col, ok, value):
   df[col] = df[col].astype(value)
   return df


def dtype_category(df, col):
   df[col].dtype == 'category'
   return ok


def to_category(df, col):
   out = df[col].astype('category')
   return out


def dtype_date(df, col):
   df[col].dtype == 'datetime64[ns]'
   return ok


def to_date(df, col):
   out = pd.to_datetime(df[col])
   return out


def is_int(df, col):
   ok = (df[col].mod(1) == 0)
   return ok


def to_int(df, col):
   out = df[col].to_numeric()
   return out


def dtype_bool(df, col):
   ok = df[col].dtype == 'bool'
   return ok


def to_bool(df, col):
   out = df[col].astype('bool')
   return out


def one_of(df, col, valid=None):
   ok = df[col].isin(valid)
   return ok


def evaluate(df, col=None, expr=None):
   all_cols = set(df.columns)
   if expr.startswith("df.") or expr.startswith('df['):
       if col:
           expr = expr.replace("[col]", f"['{col}']")  # maybe require @col?

       all_words = set(re.findall(r'\w+', expr))
       # exclude_words = {'not', 'and', 'or'}
       included_cols = list(all_cols.intersection(all_words))

       nans = df[included_cols].isnull().any(axis=1)
       # nan_evals = [f"({col}!={col})" for col in included_cols]
       # nan_evals = ' or '.join(nan_evals)
       # print(nan_evals)
       # nans = df.eval(nan_evals)
       # nans = df.eval(nan_evals)

       ok = pd.eval(expr=expr, engine='python')
       ok_wo_nan = (ok | nans)
   else:
       ok_wo_nan = df.eval(expr=expr)
   return ok_wo_nan


def length(df, col=None, equal=None, minimum=None, maximum=None):
   length = df[col].str.len()
   if equal:
       ok = (length.eval == equal)
   elif minimum and maximum:
       ok = (length.eval >= minimum) & (length.eval <= maximum)
   elif minimum:
       ok = (length.eval >= minimum)
   elif maximum:
       ok = (length.eval <= maximum)
   else:
       print("Error: Must specify one of the argument minimum, maximum, or equal")

   return ok


def upper_case(df, col=None):
   ok = df[col].str.isupper()
   return ok


def to_upper_case(df, col=None, ok=None):
   df[col] = df[col].str.upper()
   return df


def lower_case(df, col=None):
   ok = df[col].str.islower()
   return ok


def to_lower_case(df, col=None):
   df[col] = df[col].str.lower()
   return df


def stable(df, col, pid='pid'):
   ok = df.groupby(pid)[col].nunique() < 2
   return ok



def insert(df, col=None, rows, value):
   df.loc[rows, col] = value
   return df


def insert_missing(df, col=None, rows, value):
   df.loc[rows, col] = np.nan
   return df


def delete_rows(df, col=None, rows, value):
   df.loc[rows, col] = value
   return df


def valid(df, col, values, sep=None):
   """
   Check if column contain only certain values and no other
   """
   invalid = ~df[col].isin(values)
   return invalid


def minmax(df, col, min, max):
   outside = df[~df[col].between(left=min, right=max)]
   outside_values = outside[col].unique()
   outside_n = len(outside)
   outside_pid = outside.index.unique()
   return outside_values


def if_patient_has_x_then_never_y(df, x, xcol, y, ycol, z, row=False):
   incompatible = use_expression(f'{x} in {icol} and {y} in {ycol}')]
   incompatible = df[incompatible]
   return incompatible


def if_patient_has_x_then_always_also_y(df, x, y, xcol, ycol):
   x_not_y = df.use_expression(f'{x} and not {y})
   return df[x_not_y]


def if_event_has_x_then_never_y(df, x, xcol, y, ycol, z, row=False):
   incompatible = df.query(f'{x} in {icol} and {y} in {ycol}')]
   incompatible = df[incompatible]
   return incompatible


def no_missing(df, col):
   missing = df[col].isnull()
   missing = df[missing]
   return missing


def is_int(df, col):
   id_int = df[col].apply(float.is_integer)
   not_int = df[not is_int]
   return not_int


def never_decrease(df, col, sortby=None):
   sub = df
   if sort:
       sub = sub[col].sort_values(sort)
   mono = df.groupby(pid)[col].apply(x.is_monotonically)
   not_mono = df[~mono]
   return not_mono


def always_increase(df, col, sortby=None):
   sub = df
   if sort:
       sub = sub[col].sort_values(sort)
   mono = df.groupby(pid)[col].apply(x.is_monotonically)
   mono = df[mono]
   return mono


def length(df, col, min, max):
   length = df[col].astype(str).apply(len)
   length.between(min, max)


## actions
def to_int(df, col, errors='coerce'):
   s = pt.to_numeric(df[col], downcast='int', errors=errors)
   return s


def to_float(df, col, errors='coerce'):
   s = pt.to_numeric(df[col], downcast='float', errors=errors)
   return s


def to_dtype(df, col, dtype):
   df[col] = pt.to_numeric(df[col], downcast='int')
   return df[col]


def replace(df, col, to_values, **kwargs):
   s = df[col].replace(to_values, **kwargs)
   return s


def invalid2nan(df, col, invalid):
   """
   Replace invalid vaules with missing
   """
   s = df[col][invalid] = np.nan
   return s



def dropif(df, col, values):
   outside = df[~df[col].between(left=min, right=max)]
   outside_values = outside[col].unique()
   outside_n = len(outside)
   outside_pid = outside.index.unique()
   return outside_values


def convert(df, col, values):
   outside = df[~df[col].between(left=min, right=max)]
   outside_values = outside[col].unique()
   outside_n = len(outside)
   outside_pid = outside.index.unique()
   return outside_values

