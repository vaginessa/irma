#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import os

from datetime import datetime
from lib.common.utils import timestamp
from lib.plugin_result import PluginResult
from lib.common.hash import sha256sum


class AntivirusPluginInterface(object):
    """Antivirus Plugin"""

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_display_name,
                               type=type(self).plugin_category,
                               version=self.module.version)
        try:
            # add database metadata
            results.database = None
            if self.module.database:
                results.database = dict()
                for filename in self.module.database:
                    results.database[filename] = self.file_metadata(filename)
            # launch an antivirus scan, automatically append scan results
            started = timestamp(datetime.utcnow())
            results.status = self.module.scan(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            # as only one result is expected, we simply remove the filename
            # and we return the result got
            return_results = list(self.module.scan_results.values())[0]
            # add scan results or append error
            if results.status < 0:
                results.error = return_results
            else:
                results.results = return_results

            # Add virus_database_version metadata
            results.virus_database_version = self.module.virus_database_version
        except Exception as e:
            results.status = -1
            results.error = str(e)
        return results

    @staticmethod
    def file_metadata(filename):
        result = dict()
        if os.path.exists(filename):
            result['mtime'] = os.path.getmtime(filename)
            result['ctime'] = os.path.getctime(filename)
            try:
                with open(filename, 'rb') as fd:
                    result['sha256'] = sha256sum(fd)
            except Exception:
                result['sha256'] = None
        return result
