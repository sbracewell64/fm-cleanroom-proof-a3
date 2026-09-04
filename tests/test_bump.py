"""Tests for fmproof.semver.bump."""

import unittest

from fmproof.semver import InvalidVersionError, bump, parse


class BumpCorePartTest(unittest.TestCase):
    def test_major_bump_resets_minor_and_patch(self):
        self.assertEqual(bump("1.2.3", "major"), "2.0.0")

    def test_minor_bump_resets_patch_and_keeps_major(self):
        self.assertEqual(bump("1.2.3", "minor"), "1.3.0")

    def test_patch_bump_keeps_major_and_minor(self):
        self.assertEqual(bump("1.2.3", "patch"), "1.2.4")

    def test_bump_from_all_zero(self):
        self.assertEqual(bump("0.0.0", "major"), "1.0.0")
        self.assertEqual(bump("0.0.0", "minor"), "0.1.0")
        self.assertEqual(bump("0.0.0", "patch"), "0.0.1")

    def test_large_numbers_are_numeric_not_lexical(self):
        # A lexical increment would carry wrongly; 9 -> 10 proves it is numeric.
        self.assertEqual(bump("1.9.0", "minor"), "1.10.0")
        self.assertEqual(bump("9.9.9", "major"), "10.0.0")


class BumpClearsPrereleaseTest(unittest.TestCase):
    def test_major_bump_drops_prerelease(self):
        self.assertEqual(bump("1.0.0-alpha", "major"), "2.0.0")

    def test_minor_bump_drops_prerelease(self):
        self.assertEqual(bump("1.2.3-rc.1", "minor"), "1.3.0")

    def test_patch_bump_drops_prerelease(self):
        self.assertEqual(bump("1.2.3-rc.1", "patch"), "1.2.4")

    def test_dotted_prerelease_dropped(self):
        self.assertEqual(bump("2.0.0-x.7.z.92", "patch"), "2.0.1")


class BumpUnknownPartTest(unittest.TestCase):
    def test_unknown_part_raises_value_error(self):
        with self.assertRaises(ValueError):
            bump("1.2.3", "build")

    def test_unknown_part_message_names_the_part(self):
        with self.assertRaises(ValueError) as ctx:
            bump("1.2.3", "PATCH")  # case-sensitive: not one of the accepted parts
        self.assertIn("PATCH", str(ctx.exception))

    def test_empty_part_rejected(self):
        with self.assertRaises(ValueError):
            bump("1.2.3", "")


class BumpInvalidVersionTest(unittest.TestCase):
    def test_leading_v_raises_same_error_as_parse(self):
        with self.assertRaises(InvalidVersionError):
            parse("v1.2.3")
        with self.assertRaises(InvalidVersionError):
            bump("v1.2.3", "patch")

    def test_build_metadata_rejected(self):
        with self.assertRaises(InvalidVersionError):
            bump("1.0.0+build.5", "patch")

    def test_partial_version_rejected(self):
        with self.assertRaises(InvalidVersionError):
            bump("1.2", "major")

    def test_non_string_rejected(self):
        with self.assertRaises(InvalidVersionError):
            bump(123, "patch")


class BumpCompositionTest(unittest.TestCase):
    def test_repeated_bumps_follow_semver_ordering(self):
        v = "1.4.2-rc.1"
        v = bump(v, "patch")
        self.assertEqual(v, "1.4.3")
        v = bump(v, "minor")
        self.assertEqual(v, "1.5.0")
        v = bump(v, "major")
        self.assertEqual(v, "2.0.0")


if __name__ == "__main__":
    unittest.main()
