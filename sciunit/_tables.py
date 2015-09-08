"""Code for generating table views of score matrices."""

try:
  # For table generation support, cf ScoreMatrix.view
  from IPython.display import HTML
  _IPython_installed = True
except ImportError:
  _IPython_installed = False
else:
  import string
  def generate_ipy_table(sm):
  	"""Generates an IPython score table, given a score matrix.

  	Called by the ScoreMatrix.view() method.
  	"""
  	if not _IPython_installed:
  	  raise Exception("IPython not installed.")
  	return HTML(generate_table(sm))

  def generate_table(sm):
  	"""Generates the source code for the score table."""
  	return """
  	<table>
  	  {header}
  	  {body}
  	</table>""".format(
      header = _generate_header(sm),
      body = _generate_body(sm)
  	)

  def _generate_header(sm):
    return "<thead><tr><th></th>{columns}</tr></thead>".format(
    	columns='\r'.join(
          "<th>%s</th>" % str(test)
          for test in sm.tests
        ))

  def _generate_body(sm):
    return "<tbody>{rows}</tbody>".format(
      rows = '\r'.join(
        "<tr><td>{model}</td>{scores}</tr>".format(
          model=str(model), 
          scores=_generate_row(sm, model))
        for model in sm.models
    ))

  def _generate_row(sm, model):
    return '\r'.join(
      "<td>{score}</td>".format(score=str(score))
      for score in sm[model].scores)
