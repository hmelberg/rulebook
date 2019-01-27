# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 23:31:49 2018

@author: hmelberg_adm
"""

import numpy as np
import pandas as pd
import copy
import pickle
import re


# %%

class OneRule():
   def __init__(self, text, name, group, func, args=None, action=None,
                action_args=None, etc=None):
       self.text = text,
       self.name = name,
       self.group = group,
       self.func = func,
       self.args = args,
       self.action = action,
       self.action_args = action_args,
       self.etc = etc


# %%
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


# %%
class RuleGroup():
   def __init__(self, rules, cols=None, name=None,
                description=None, action=None, comments=None, etc=None):
       self.rules = _listify(rules)
       self.cols = _listify(cols)
       self.name = name
       self.description = description
       self.action = action
       self.comments = comments
       self.etc = etc


# %%
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


# %%
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


# %%
class RuleBook():
   def __init__(self, rules=None):
       self.rulebook_list = list()
       self.comments = None,
       self.info = None,

   def add(self, rules, cols=None, name=None, description=None,
           action=None, comments=None, etc=None):
       """
       Adds a rule object (one or more rules) to the rulebook

       args:
           - rule (str, list of str): The name of the function determining valid observations
                   - can use inbuilt functions of self-defined functions
                   - can add arguments to functions in parenthesis, but must use keywords
                   - can use a list of one or more functions and columns: one or multiple rules can apply to one or more columns
                   - the function should return a series with 1 for valid rows and 0 for invalid rows (missing = invalid = false = 0)
           - cols (str, list of str): The column(s) where the rule(s) apply
                   - Single columns can be a str, and a comma seperated str is converted to a list with mupliple cols
           - name (str, optional): The rule can be assigned a name. if no name is assigned, one will e autogenerated (rule_1 etc)
           - description (str, optional): Describe rule in more detail
           - action (str, list of str): The name  of the function to be used  if rule is violated  (arguments in allowed in parenthesis)

       examples
           - add('is_int', 'age')
           - add(['is_int', 'is_positive'], ['age', 'days'])
           - add('length(max=5)', 'icd')

       """

       rule_group = RuleGroup(rules=rules, cols=cols, name=name, description=description,
                              action=action, comments=comments, etc=etc)

       # give the rule a name if no name is given
       if not rule_group.name:
           nrules = len(self.rulebook_list)
           proposed_name = 'rule_' + str(nrules + 1)
           existing_names = [rule.name for rule in self.rulebook_list]

           if proposed_name in existing_names:
               existing_nums = [int(name.split('_')[1]) for name in existing_names if
                                'rule_' in name]  # potentialproblem a name such as rule_no_negative
               max_num = max(existing_nums)
               proposed_name = 'rule_' + str(max_num + 1)
           rule_group.name = proposed_name

       # convert col to list if it is a string with , inside
       if rule_group.cols:
           if ',' in rule_group.cols:
               cols = rule.cols.split(',')
               cols = [strip(col) for col in cols]
               rule_group.cols = cols

       setattr(self, rule_group.name, rule_group)
       self.rulebook_list.append(rule_group)

   def add_many(self, rules):
       """
       add many rules to the rule object

       Note
           - Only works when column name is part of the expressions (ie. not with functions since functions also need to be assigned to columns)
           - Both a list and a comma separated string is ok

           add_many('age>18, birth_year>1970')
           add_many(['age>18', 'birth_year>1970'])
       """

       if isinstance(rules, str):
           rules = rules.split(',')
       for rule in rules:
           self.add(rule=rule)

   def delete(self, rules):
       if isinstance(rules, str): rules = set([rules])
       keep_rules = [rule for rule in self.rules if rule.name not in rules]
       self.rules = keep_rules

   def append_col(self, name, cols):
       cols = listify_cols
       modified_rules = []
       for rule in self.rulebook_list:  # rulebook_lilst should be private  .. and called sth else
           if rule.name == name:
               rule.cols.extend(cols)
           modified_rules.append(rule)
       return modified_rules

   def drop_col(self, name, cols):
       cols = listify_cols
       modified_rules = []
       for rule in self.rulebook_list:  # rulebook_lilst should be private  .. and called sth else
           if rule.name == name:
               existing_cols = rule.cols
               keep_cols = existing_cols - set(cols)
               rule.cols = keep_cols
           modified_rules.append(rule)
       return modified_rules

   def view(self, rules=None):
       if not rules: rules = self.rulebook_list
       for rule in rules:
           print(rule.name, rule.rules)

   def view_cols(self, cols=None, rules=None):
       self._fix_format()

       if not rules: rules = self.rulebook_list

       col_rules = {}
       for rule in rules:
           for col in rule.cols:
               if (not cols) or (cols in rule.cols):
                   if col in col_rules:
                       col_rules[col].append(rule)
                   else:
                       col_rules[col] = [rule]

       for col, rules in col_rules.items():
           for rule in rules:
               print(col, rule.name, rule.rule)

   def save(self, file):
       with open(file, 'wb') as output:
           pickle.dump(self, output, protocol=0)
           # pickle.HIGHEST_PROTOCOL

   def _check(self, df, rules=None, cols=None, change=False, out='check'):

       # use all or only some rules
       all_rules = set(self.rulebook_list)
       all_names = set([rule.name for rule in all_rules])

       if rules:
           specified_names = set(_listify(rules))
           subset_names = all_names.intersection(specified_names)
       else:
           subset_names = all_names

       subset_rules = [rule for rule in all_rules if rule.name in subset_names]

       # use all or only some columns
       if cols:
           subset_rules = copy.deepcopy(subset_rules)
           include_cols = set(cols)

           for rule in subset_rules:
               existing_cols = set(rule.cols)
               new_cols = existing_cols.intersection(include_cols)
               rule.cols = list(new_cols)

       # same rule(s) may apply to many column(s), so make
       # separate rule for each combination
       expanded_rules = _expand_rulelist(subset_rules)

       # dictionary to save info from check
       result = {}

       for rule in expanded_rules:
           ok = globals()[rule.func[0]](df=df, **rule.args[0])  # hmmm why are these tuples?)

           if rule.args[0]['col']:
               col = rule.args[0]['col']
               name = f"{rule.name}_col{col}"

               result[name] = dict()
               result[name]['ok'] = ok
               result[name]['nans'] = df[col].isnull().sum()
               result[name]['ninvalid'] = (~ok).sum()
               result[name]['values'] = df[col][~ok].values
               result[name]['series'] = df[col][~ok]
               result[name]['df'] = df[~ok]
           else:
               result[rule.name] = dict()

               result[name]['ok'] = ok
               result[name]['nans'] = ok.isnull().sum()
               result[name]['ninvalid'] = (~ok).sum()
               result[name]['df'] = df[~ok]

           # change the column(s)
           if change and rule.action:
               try:
                   new_df = globals()[rule.action[0]](df=df, ok=ok, **rule.action_args[0])
               except:
                   print(f"Error for rule {rule.name, rule.text}")

       if out == 'check':
           for name, res in result.items():
               print(name, res['ninvalid'], res['nans'])
           return result
           # return fails

       elif out == 'change':
           return new_df
       elif out == 'check_and_change':
           return result, df
       else:
           print('out argument is wrong')
       return

   def check(self, df, rules=None, cols=None):
       results_out = self._check(df=df, rules=rules, cols=cols, out='check')
       return results_out

   def change(self, df, rules=None, cols=None):
       changed_df = self._check(df=df, rules=rules, cols=cols, out='change', change=True)
       return changed_df

   def check_change_check(self, df, rules=None, cols=None):
       df_with_fails_before = self._check(df=df, rules=rules, cols=cols)
       changed_df = self._check(df=df, rules=rules, cols=cols, out='change')
       df_with_fails_after = self._check(df=changed_df, rules=rules, cols=cols)
       return changed_df, df_with_fails_before, df_with_fails_after









