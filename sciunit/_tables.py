"""Code for generating table views of score matrices."""
"""DEPRECATED"""
#import sciunit.scores

try:
  import pandas as pd
  pd.set_option('precision',3)
except ImportError:
  _pandas_installed = False
else:
  _pandas_installed = True
  def generate_df(sm, mean=False, css=""):
    if not _pandas_installed:
      raise Exception("Pandas not installed.")
    df = pd.DataFrame(sm.scores,index=sm.tests,columns=sm.models).T
    df.loc[:,'Mean'] = [sm.mean_score(m) for m in sm.models]
    cols = list(df)
    cols.insert(0, cols.pop(cols.index('Mean')))
    df = df.reindex(columns=cols)
    return(df)

try:
  # For table generation support, cf ScoreMatrix.view
  from IPython.display import HTML,Javascript,display
  _IPython_installed = True
except ImportError:
  _IPython_installed = False
else:
  import string
  def generate_ipy_table(sm, mean=False, css=""):
    """Generates an IPython score table, given a score matrix.
    Called by the ScoreMatrix.view() method.
    """
    if not _IPython_installed:
      raise Exception("IPython not installed.")
    
    html_src = """
      <style>
        th {{
          align:center;
          font-size:75%;
          }}
        {css}
      </style>
      {table}
    """.format(id=hash(sm), css=css, table=generate_table(sm, mean=mean))
    html = HTML(html_src)

    js_src = """
      $('.datatable').dataTable();
    """

    js = Javascript(js_src,
      lib=["//ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.0/jquery.dataTables.min.js"],
      css=["//ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.0/css/jquery.dataTables.css"])
    
    display(html,js)
    
  def generate_table(sm, mean=False):
    """Generates the source code for the score table."""
    return """
      <table id={id} class='datatable'>
        {header}
        {body}
      </table>
    """.format(
      id = hash(sm),
      header = _generate_header(sm, mean=mean),
      body = _generate_body(sm, mean=mean)
    )

  def _generate_header(sm, mean=False):
    return """
      <thead>
        <tr>
          <th></th>
          {mean_column}
          {columns}
        </tr>
      </thead>
    """.format(
      mean_column='<th>Mean</th>' if mean else '',
      columns='\r'.join(
          "<th>%s</th>" % str(test)
          for test in sm.tests
        ))

  def _generate_body(sm, mean=False):
    return """
      <tbody>
        {rows}
      </tbody>
    """.format(
      rows = '\r'.join(
        "<tr><td>{model}</td>{scores}</tr>".format(
          model=str(model), 
          scores=_generate_row(sm, model, mean=mean))
        for model in sm.models
    ))

  def _generate_row(sm, model, mean=False):
    html = '\r'.join("""<td style='background-color: rgb{rgb};'>
                          <p hidden>{sort_key}</p>{score}
                        </td>
                      """.format(
                      sort_key='%.4f' % (0.0 if score.sort_key is None else score.sort_key),
                      rgb=str(score_to_rgb(score)),
                      score=score)\
                        for score in sm[model].scores)
    if mean:
      mean_score = sm.mean_score(model)
      html = """<td style='background-color: rgb{rgb};'>
                  {score}
                </td>
              """.format(
                rgb=str(score_to_rgb(mean_score, raw=True)),
                score='%.3f' % mean_score) + html
    return html

  def score_to_rgb(score, raw=False, gamma=0.8):
    """Converts a score to an RGB triplet (0-255)."""

    import math
    value = score if raw else score.sort_key
    if value is not None and not math.isnan(value):
      #wavelength = 380 + score.sort_key*(750-380)
      r = 255
      g = int(255 * value)
      b = int(255 * value)
      #wavelength_to_rgb(wavelength,gamma)
    else:
      r,g,b = 128,128,128
    return r,g,b
