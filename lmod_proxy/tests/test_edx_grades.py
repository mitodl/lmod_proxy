# -*- coding: utf-8 -*-
"""Unit testing for the edx_grades blueprint"""
import copy
import json
import logging
import unittest

import mock
from pylmod.exceptions import PyLmodException

import lmod_proxy.web


logging.basicConfig(level=logging.DEBUG)


class TestEdXGrades(unittest.TestCase):
    """
    Primary test class for testing edX grades.
    """
    FULL_FORM = dict(
        gradebook='test_gradebook',
        user='user@example.com',
        datafile='a,b,c',
        section='test_section',
        submit='get-membership'
    )

    EDX_GRADE_URL = '/edx_grades'

    def setUp(self):
        """Setup commonly needed objects like the flask test client"""
        super(TestEdXGrades, self).setUp()
        self.client = lmod_proxy.web.app.test_client()

    def test_form(self):
        """Verify the form has all the fields as we expect it"""
        from lmod_proxy.edx_grades.forms import EdXGradesForm
        # Fully filled out form.
        form = EdXGradesForm(**self.FULL_FORM)
        self.assertTrue(form.validate())

        # Make sure optional stuff is optional
        local_form = copy.deepcopy(self.FULL_FORM)
        del local_form['section']
        del local_form['datafile']
        form = EdXGradesForm(**local_form)
        self.assertTrue(form.validate())

        # Make sure required stuff is required
        local_form = copy.deepcopy(self.FULL_FORM)
        del local_form['user']
        form = EdXGradesForm(**local_form)
        self.assertFalse(form.validate())

        local_form = copy.deepcopy(self.FULL_FORM)
        del local_form['submit']
        form = EdXGradesForm(**local_form)
        self.assertFalse(form.validate())

        local_form = copy.deepcopy(self.FULL_FORM)
        del local_form['gradebook']
        form = EdXGradesForm(**local_form)
        self.assertFalse(form.validate())

        # Verify user must be email
        local_form = copy.deepcopy(self.FULL_FORM)
        local_form['user'] = 'foo'
        form = EdXGradesForm(**local_form)
        self.assertFalse(form.validate())

        # Verify submit choices
        local_form = copy.deepcopy(self.FULL_FORM)
        local_form['submit'] = 'not-real'
        form = EdXGradesForm(**local_form)
        self.assertFalse(form.validate())

        # Verify we strip spaces
        local_form = copy.deepcopy(self.FULL_FORM)
        strip_key_list = ('user', 'gradebook', 'datafile', 'section')
        for key in strip_key_list:
            local_form[key] = ' {0} '.format(local_form[key])

        form = EdXGradesForm(**local_form)
        form.validate()

        print form.data
        for key, item in form.data.items():
            self.assertEqual(self.FULL_FORM[key], item)

    @mock.patch('lmod_proxy.edx_grades.log')
    def test_get_root(self, log):
        """Test the GET response returns what we want"""
        response = self.client.get(
            self.EDX_GRADE_URL,
            headers={'X-Forwarded-For': ['abc']}
        )
        self.assertEqual(200, response.status_code)
        log.info.assert_assert_called_with(
            'edX remote gradebook GET request from %s',
            'abc'
        )

    def test_bad_post(self):
        """Verify we get a json response with an error when we POST bad data"""
        local_form = copy.deepcopy(self.FULL_FORM)
        del local_form['user']

        response = self.client.post(self.EDX_GRADE_URL, data=local_form)
        self.assertEqual(422, response.status_code)
        self.assertEqual(
            json.loads(response.data),
            {
                'msg': ('Malformed API Call: {\'user\': '
                        '[u\'Invalid email address.\']}'),
                'data': [],
            }
        )

    @mock.patch('lmod_proxy.edx_grades.GradeBook')
    def test_post_actions(self, patched_gradebook):
        """Verify that we call the right functions with each action type"""
        local_form = copy.deepcopy(self.FULL_FORM)

        from lmod_proxy.edx_grades.forms import ACTIONS
        action_list = ACTIONS.keys()
        mock_instrumented_actions = {}
        for key in action_list:
            magic = mock.MagicMock()
            magic.return_value = ('foo', ['bar'], True)
            mock_instrumented_actions[key] = magic

        # Patch the action functions to call our mock
        with mock.patch.dict(
                'lmod_proxy.edx_grades.forms.ACTIONS',
                mock_instrumented_actions
        ):
            for action in action_list:
                local_form['submit'] = action
                response = self.client.post(
                    self.EDX_GRADE_URL, data=local_form
                )
                self.assertEqual(200, response.status_code)
                self.assertTrue(mock_instrumented_actions[action].called)
                self.assertTrue(patched_gradebook.called)
                self.assertEqual(json.loads(response.data)['data'], ['bar'])

    def test_get_sections(self):
        """Test get_sections actions as expected"""
        from lmod_proxy.edx_grades.forms import EdXGradesForm
        from lmod_proxy.edx_grades.actions import get_sections

        form = EdXGradesForm(**self.FULL_FORM)
        gradebook = mock.MagicMock()
        gradebook.get_sections.return_value = 'foo'

        # Call regularly
        message, data, success = get_sections(gradebook, form)
        gradebook.get_sections.assert_called_with(simple=True)
        self.assertTrue(success)
        self.assertEqual(data, 'foo')

        # Now raise an expected exception
        gradebook.get_sections.side_effect = PyLmodException('test')
        message, data, success = get_sections(gradebook, form)
        gradebook.get_sections.assert_called_with(simple=True)
        self.assertFalse(success)
        self.assertEqual(message, 'test')
        self.assertEqual(data, [{}])

    def test_get_assignments(self):
        """Test get_assignments actions as expected"""
        from lmod_proxy.edx_grades.forms import EdXGradesForm
        from lmod_proxy.edx_grades.actions import get_assignments

        form = EdXGradesForm(**self.FULL_FORM)
        gradebook = mock.MagicMock()
        gradebook.get_assignments.return_value = 'foo'

        # Call regularly
        message, data, success = get_assignments(gradebook, form)
        gradebook.get_assignments.assert_called_with(simple=True)
        self.assertTrue(success)
        self.assertEqual(data, 'foo')

        # Now raise an expected exception
        gradebook.get_assignments.side_effect = PyLmodException('test')
        message, data, success = get_assignments(gradebook, form)
        gradebook.get_assignments.assert_called_with(simple=True)
        self.assertFalse(success)
        self.assertEqual(message, 'test')
        self.assertEqual(data, [{}])

    def test_get_membership(self):
        """Test get_assignments actions as expected"""
        from lmod_proxy.edx_grades.forms import EdXGradesForm
        from lmod_proxy.edx_grades.actions import get_membership

        form = EdXGradesForm(**self.FULL_FORM)
        gradebook = mock.MagicMock()
        gradebook.get_students.return_value = 'foo'

        # Call regularly
        message, data, success = get_membership(gradebook, form)
        gradebook.get_students.assert_called_with(
            simple=True,
            section_name=self.FULL_FORM['section']
        )
        self.assertTrue(success)
        self.assertEqual(data, 'foo')

        # Now raise an expected exception
        gradebook.get_students.side_effect = PyLmodException('test')
        message, data, success = get_membership(gradebook, form)
        gradebook.get_students.assert_called_with(
            simple=True,
            section_name=self.FULL_FORM['section']
        )
        self.assertFalse(success)
        self.assertEqual(message, 'test')
        self.assertEqual(data, [{}])

    @mock.patch('lmod_proxy.edx_grades.actions.StringIO')
    def test_post_grades(self, mock_io):
        """Test post_grades actions as expected"""
        from lmod_proxy.edx_grades.forms import EdXGradesForm
        from lmod_proxy.edx_grades.actions import post_grades

        form = EdXGradesForm(**self.FULL_FORM)
        gradebook = mock.MagicMock()
        gradebook_return = {'data': {'test': 'foo'}}
        gradebook.spreadsheet2gradebook.return_value = (gradebook_return, 1)

        # Call regularly
        message, data, success = post_grades(gradebook, form)
        self.assertTrue(gradebook.spreadsheet2gradebook.called)
        mock_io.assert_called_with(self.FULL_FORM['datafile'])
        self.assertEqual(data, [])

        # Now raise an expected exception
        self.assertTrue(success)
        gradebook.spreadsheet2gradebook.side_effect = PyLmodException('test')
        message, data, success = post_grades(gradebook, form)
        self.assertTrue(gradebook.spreadsheet2gradebook.called)
        mock_io.assert_called_with(self.FULL_FORM['datafile'])
        self.assertFalse(success)
        self.assertEqual(message, 'test')
        self.assertEqual(data, [])

        # Now fail a few grades
        gradebook_return['data']['numFailures'] = 100
        gradebook_return['data']['results'] = ['completely unexpected']
        gradebook.spreadsheet2gradebook.side_effect = None

        with mock.patch(
                'lmod_proxy.edx_grades.actions.render_template'
        ) as mock_template:
            message, data, success = post_grades(gradebook, form)
            self.assertTrue(gradebook.spreadsheet2gradebook.called)
            mock_io.assert_called_with(self.FULL_FORM['datafile'])
            mock_template.assert_called_with(
                'grade_transfer_failed.html',
                number_failed=100,
                failed_grades=['completely unexpected']
            )
            self.assertFalse(success)
            self.assertEqual(data, [])

    def test_template_existence(self):
        """Just an OS test that the templates we need exist"""
        template_list = [
            'grade_transfer_failed.html',
            'api_message.html',
            'index.html',
        ]

        from lmod_proxy.edx_grades import edx_grades
        for template in template_list:
            edx_grades.open_resource('templates/edx_grades/{0}'.format(
                template
            ))
