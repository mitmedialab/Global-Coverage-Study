#! /usr/bin/env python

import unittest

from media.test.sourcetest import MediaSourceCollectionTest

suite = unittest.TestLoader().loadTestsFromTestCase(MediaSourceCollectionTest)
unittest.TextTestRunner(verbosity=2).run(suite)
