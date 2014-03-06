#! /usr/bin/env python

import unittest

from dashboard.test.sourcetest import MediaSourceCollectionTest

suite = unittest.TestLoader().loadTestsFromTestCase(MediaSourceCollectionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
