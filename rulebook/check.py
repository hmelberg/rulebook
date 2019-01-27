# functions that check a condition
# returns a boolean series indicating whether the check is OK or not

def stable(df, col, pid='pid'):
    """
    checks whether the values in the column is unique for each group

    returns a boolean series with zero for rows in the column not listed in values
    """
    ok = df.groupby(pid)[col].nunique() < 2
    return ok

def between(df,col, lower, upper):
    ok = (df[col]>=lower & df[col]<=upper)
    return ok

def one_of(df, col, values=None, sep=None):
    """
    checks whether the rows in the column also is listed in values

    returns a boolean series with zero for rows in the column not listed in values
    """
    if sep:
        expanded_df=df[col].str.split(sep=sep, expand=True)
        ok=expanded_df.isin(values).all(axis=1)
    else:

        ok = df[col].isin(values)
    return ok

def contains(df, col, text, case=True, flags=int, na=True, regex=True):
    """
    checks whether strings in the column contains the specified text
    """
    ok = df[col].str.contains(text, case=case, flags=flags, na=na, regex=regex)  # note na true, discuss!
    return ok

def not_contain(df, col, text, case=True, flags=int, na=True, regex=True):
    not_ok = df[col].str.contains(text, case=case, flags=flags, na=na, regex=regex)
    ok = ~ not_ok
    return ok

def evaluate(df, col=None, expr=None):
    """
    if expr startswith "df." or "df[" use pd.eval on the expr, else uses df.eval(expr)

    Returns: A series with zero where the expression is false

    """
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
    """
    Check if length of string  in column is smaller, equal, or larger than a value

    Returns: Boolean series with zero for rows where the condition is not met
    """
    lengths = df[col].str.len()
    if equal:
        ok = (lengths.eval == equal)
    elif minimum and maximum:
        ok = (lengths.eval >= minimum) & (lengths.eval <= maximum)
    elif minimum:
        ok = (lengths.eval >= minimum)
    elif maximum:
        ok = (lengths.eval <= maximum)
    else:
        print("Error: Must specify one of the argument minimum, maximum, or equal")

    return ok

def upper_case(df, col=None):
   ok = df[col].str.isupper()
   return ok

def lower_case(df, col=None):
   ok = df[col].str.islower()
   return ok


def no_missing(df, col):
   missing = df[col].isnull()
   missing = df[missing]
   return missing

# hmm these do not return a series, but a scalar

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

