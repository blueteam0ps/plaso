# -*- coding: utf-8 -*-
"""The analysis plugin mediator object."""

import time

from plaso.containers import warnings
from plaso.engine import path_helper


class AnalysisMediator(object):
  """Analysis plugin mediator.

  Attributes:
    last_activity_timestamp (int): timestamp received that indicates the last
        time activity was observed. The last activity timestamp is updated
        when the mediator produces an attribute container, such as an event
        tag. This timestamp is used by the multi processing worker process
        to indicate the last time the worker was known to be active. This
        information is then used by the foreman to detect workers that are
        not responding (stalled).
    number_of_produced_analysis_reports (int): number of produced analysis
        reports.
    number_of_produced_event_tags (int): number of produced event tags.
  """

  def __init__(self, storage_writer, knowledge_base, data_location=None):
    """Initializes an analysis plugin mediator.

    Args:
      storage_writer (StorageWriter): storage writer.
      knowledge_base (KnowledgeBase): contains information from the source
          data needed for analysis.
      data_location (Optional[str]): location of data files used during
          analysis.
    """
    super(AnalysisMediator, self).__init__()
    self._abort = False
    self._data_location = data_location
    self._event_filter_expression = None
    self._knowledge_base = knowledge_base
    self._number_of_warnings = 0
    self._storage_writer = storage_writer

    self.last_activity_timestamp = 0.0
    self.number_of_produced_analysis_reports = 0
    self.number_of_produced_event_tags = 0

  @property
  def abort(self):
    """bool: True if the analysis should be aborted."""
    return self._abort

  @property
  def data_location(self):
    """str: path to the data files."""
    return self._data_location

  @property
  def operating_system(self):
    """str: operating system or None if not set."""
    return self._knowledge_base.GetValue('operating_system')

  def GetDisplayNameForPathSpec(self, path_spec):
    """Retrieves the display name for a path specification.

    Args:
      path_spec (dfvfs.PathSpec): path specification.

    Returns:
      str: human readable version of the path specification.
    """
    mount_path = self._knowledge_base.GetMountPath()
    text_prepend = self._knowledge_base.GetTextPrepend()
    return path_helper.PathHelper.GetDisplayNameForPathSpec(
        path_spec, mount_path=mount_path, text_prepend=text_prepend)

  def GetUsernameForPath(self, path):
    """Retrieves a username for a specific path.

    This is determining if a specific path is within a user's directory and
    returning the username of the user if so.

    Args:
      path (str): path.

    Returns:
      str: username or None if the path does not appear to be within a user's
          directory.
    """
    return self._knowledge_base.GetUsernameForPath(path)

  def ProduceAnalysisReport(self, plugin):
    """Produces an analysis report.

    Args:
      plugin (AnalysisPlugin): plugin.
    """
    analysis_report = plugin.CompileReport(self)
    if not analysis_report:
      # TODO: produce AnalysisWarning that no report can be generated.
      return

    analysis_report.event_filter = self._event_filter_expression

    self._storage_writer.AddAnalysisReport(analysis_report)

    self.number_of_produced_analysis_reports += 1
    self.number_of_produced_event_tags = (
        self._storage_writer.number_of_event_tags)

    self.last_activity_timestamp = time.time()

  def ProduceAnalysisWarning(self, message, plugin_name):
    """Produces an analysis warning.

    Args:
      message (str): message of the warning.
      plugin_name (str): name of the analysis plugin to which the warning
          applies.
    """
    warning = warnings.AnalysisWarning(message=message, plugin_name=plugin_name)
    self._storage_writer.AddAnalysisWarning(warning)
    self._number_of_warnings += 1

    self.last_activity_timestamp = time.time()

  def ProduceEventTag(self, event_tag):
    """Produces an event tag.

    Args:
      event_tag (EventTag): event tag.
    """
    self._storage_writer.AddEventTag(event_tag)

    self.number_of_produced_event_tags += 1

    self.last_activity_timestamp = time.time()

  def SignalAbort(self):
    """Signals the analysis plugins to abort."""
    self._abort = True
