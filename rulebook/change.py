
# functions that change invalid observations and return a changed dataframe

def del_row(df, col=None, ok=None):
   """
   deletes a row with invalid values
   """
   df = df[ok]
   return df


def to_nan(df, col=None, ok=None):
   """
   replaces invalid values with missing (NaN)
   """
   df.loc[~ ok, col] = np.nan
   return df


def insert(df, col=None, , ok=None, value):
   """
   replaces invalid observations with a user defined value (num or string)
   """
   df.loc[~ok, col] = value
   return df


def replace(df, col=None, ok=None, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
   df.loc[~ ok, col] = df[~ok, col].replace(to_replace=to_replace, value=value, inplace=inplace, limit=limit, regex=regex,
                             method=method)  # note na true, discuss!
   return df


def to_upper_case(df, col=None, ok=None):
   df[col] = df[col].str.upper()
   return df


def to_lower_case(df, col=None):
   df[col] = df[col].str.lower()
   return df


# change on series, not individual observations
def to_int(df, col, errors='coerce'):
   s = pt.to_numeric(df[col], downcast='int', errors=errors)
   return s


def to_float(df, col, errors='coerce'):
   s = pt.to_numeric(df[col], downcast='float', errors=errors)
   return s


def to_dtype(df, col, dtype):
   df[col] = pt.to_numeric(df[col], downcast='int')
   return df[col]