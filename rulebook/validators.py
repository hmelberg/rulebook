

# change functions


# rule functions


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


def length(df, col, min, max):
   length = df[col].astype(str).apply(len)
   length.between(min, max)


## actions


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

