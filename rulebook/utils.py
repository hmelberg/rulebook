import pickle
import re
import pandas as pd

def load_rulebook(file):
   with open(file, 'rb') as input:
       rb = pickle.load(input)
   return rb


def _find_type(rule):
   start = rule.split('(', 1)[0]

   if rule.startswith('df.'):
       rule_type = 'pd.eval'
       # func = pd.eval(), kwargs = {expression = "df.groupby...."}
   elif start in globals():
       rule_type = 'function'
       # no change!
   else:
       rule_type = 'df.eval'
       # func = df.eval(), kwargs = {expression = "age>45"}
   return rule_type


def _make_dict(kwarg_str):
   """
   Takes a string with arguments and returns a dict

   example
   >>> _make_dict("red=1, green=2, blue=3")
   >>> {'red':1, 'green':2, 'blue':3}
   >>> _make_dict("red='age', green=2, blue=3")
   >>> _make_dict("red=df, green=2, blue=3")
   """

   def _eval2dict(**kwargs):
       """
       make a dictionary from a string
       """
       return kwargs

   kwargs_dict = eval(fr"_eval2dict({kwarg_str})")
   return kwargs_dict


def _expand_rulelist(rulelist):
   """
   Expand a rulebook into many single rules

   rules: a list of rule objects

   """

   expanded_rules = []
   for rule in rulelist:
       rules = group2rules(rule)

       expanded_rules.extend(rules)

   return expanded_rules


def _expand_rules(book):
   """
   Expand a rulebook into many single rules

   rules: a list of rule objects

   """

   expanded_rules = []
   for rule in book.rulebook_list:
       rules = group2rules(rule)

       expanded_rules.extend(rules)

   return expanded_rules


def _listify(x):
   """Makes a list of everything that is not a list

   Background:
       Avoid having to use list when adding single function rules an/or single columns
       Allow add('is_int', 'age') and not require add(['is_int'], ['age'])
   """

   if not isinstance(x, list):
       x = [x]
   return x


def _insert_eval(rule):
   """
   inserts eval(expr=RULE) for rules that are expresssions and not functions

   # todo: make both single and double quotation marks work (use single now?)
   Example:
       rb.add("df.groupby('pid')['gender'].nunique()<2")
   becomes
       rb.add("evaluate(expr="df.groupby('pid')['gender'].nunique()<2")")
   why?
       standardize all rules: always start with a function
       easier to code with it
   """
   if rule.startswith('df.'):
       rule = f'evaluate(expr="{rule}")'
   elif rule.split('(')[0] in globals():
       pass
   else:
       rule = f'evaluate(expr="{rule}")'
   return rule


def _visualize(results):
   data = [(res['name'], res['nans'], res['ninvalid'])
           for name, res in results.items()]
   data = pd.DataFrame(data, columns=['name', 'missing', 'invalid'])
   data = data.set_index('name')
   fig = data.plot.barh(stacked=True)
   return fig


def _eval2cols(rule, df):
   """
   extract information about what column an expression is about

   example
       "age >0" will return ["age"]

   note_- in order to identify the column names in all the text, the daraframe is needed as input
   (and only column names that exist in the dataframe wil be returned)

   """

   rule_type = _find_type(rule)
   cols = set(df.columns)

   if rule_type != 'function':
       text = rule.text
       words = set(re.findall(r'\w+', text))
       cols = cols.intersection(words)
   return list(cols)


def suggest_rulebook(df, rules=None, cols=None, sample=0.1, pid='pid', threshold=0.1):
   """
   Suggest a rule book when almost all of the results conform to a rule
   """
   rule_col = {}
   # df = df.sample(sample)

   all_cols = list(df.columns)
   # rb = RuleBook()

   # first find dtypes
   dtypes = df.dtypes.apply(lambda x: x.name).to_dict()

   num_cols = list(df.select_dtypes(include='number').columns)
   obj_cols = list(df.select_dtypes(include='object').columns)
   date_cols = list(df.select_dtypes(include='datetime').columns)
   cat_cols = list(df.select_dtypes(include='category').columns)
   int_cols = list(df.select_dtypes(include='int').columns)
   float_cols = list(df.select_dtypes(include='float').columns)
   bool_cols = list(df.select_dtypes(include='bool').columns)
   # delta_cols
   # other_cols
   # mixed_cols

   for col in all_cols:
       rule_col[col] = [f'dtype_{dtypes[col]}']

   # find datecols
   # df.infer_objects().dtypes
   dtype = {col: [] for col in all_cols}
   obs = df.head(1000)

   obj_cat_cols = obj_cols + cat_cols

   for col in obj_cat_cols:

       ser = obs[col].dropna()

       if ser.empty or all(ser == ' '):
           continue

       print(col)
       ok = pd.to_numeric(ser, errors='coerce')
       if ok.notnull().sum() > 500:
           rule_col[col].append('dtype_num')

       ok = pd.to_datetime(ser.dropna().head(1000), errors='coerce')
       if ok.notnull().sum() > 500:
           dtype[col] = 'date'
           rule_col[col].append('dtype_date')

       uniques = ser.nunique()
       print(col, uniques)
       if uniques:
           if len(obs) / uniques > 3:
               dtype[col] = 'category'
               rule_col[col].append('dtype_category')  # and delete if existing is rule that says object

       if pid:
           ok = (obs.groupby(pid)[col].nunique() == 1)
           if ok.sum() > 0.95 * obs[pid].nunique():
               rule_col[col].append('stable')

       if ser.nunique() > 990:
           rule_col[col].append('unique')

       len_dist = ser.str.len().value_counts()
       # outliers out, frequency of ? relative to n, also dispersion in general? need measure here, statistics

       if ser.nunique() > 990:
           rule_col[col].append('unique')

   for col in num_cols:
       print(col)
       ser = obs[col].dropna()

       if ser.empty:
           continue

       if ser.nunique() < 3:
           dtype[col] = 'bool'
           rule_col[col].append('bool')

       if ser.min() > 0 and ser.max() < 1:
           rule_col[col].append('between(0,1)')

       if pid:
           ok = (obs.groupby(pid)[col].nunique() == 1)

           if ok.sum() > 0.95 * obs[pid].nunique():
               rule_col[col].append('stable')  # (maybe unique(groupby='pid'))

       if col.startswith('age'):
           rule_col[col].extend(['always_positive', "increase(groupby='pid', sort='date'), max(150)"])

       if obs[col].nunique() > 995:
           rule_col[col].append('unique')

       if col == 'pid':
           rule_col[col].append('no_missing')

       if ser.sort_values().iloc[5] >= 0:
           rule_col[col].append('is_positive')

   # add special rules - examine dtypes, max, min, contains etc

   return rb


def group2rules(rule_group):
   group_list = []
   if rule_group.action:
       action, *action_args = rule_group.action.split('(', 1)
       if action_args:
           action_args = action_args[0].strip(')')
       else:
           action_args = None
   else:
       action = None
       action_args = None

   groupname = rule_group.name

   for n, rule in enumerate(rule_group.rules):
       subname = f'{rule_group.name}_sub_{n}'
       new_rule = _insert_eval(
           rule)  # allow eval also in action functions? maybe not? or maybe ok, like df.age.replace(...)
       func, *args = new_rule.split('(', 1)
       if args:
           args = args[0].strip(')')
       else:
           args = None

       if rule_group.cols:
           for col in rule_group.cols:
               if args:
                   nargs = f"col='{col}', {args}"
               else:
                   nargs = f"col='{col}'"
               nargs = _make_dict(nargs)

               subname = f'{rule_group.name}_sub_{n}_col_{col}'

               if rule_group.action:
                   if action_args:
                       action_args = f"col='{col}', {action_args}"
                   else:
                       action_args = f"col='{col}'"
                   action_args = _make_dict(f'{action_args}')

               one_rule = OneRule(text=rule, func=func, name=subname,
                                  group=groupname, args=nargs,
                                  action=action, action_args=action_args)
               group_list.append(one_rule)

       else:
           if args:
               args = _make_dict(args)
           else:
               args = None

           if rule_group.action:
               if action_args:
                   action_args = _make_dict(f'{action_args}')
               else:
                   action_args = None

               one_rule = OneRule(text=rule, func=func, name=subname,
                                  group=groupname, args=args,
                                  action=action, action_args=action_args)
               group_list.append(one_rule)
   return group_list