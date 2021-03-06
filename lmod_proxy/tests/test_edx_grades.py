# -*- coding: utf-8 -*-
"""Unit testing for the edx_grades blueprint"""
import copy
import json
import io

import unittest.mock as mock
from pylmod.exceptions import PyLmodException
from werkzeug.datastructures import FileStorage

from lmod_proxy.edx_grades import edx_grades
from lmod_proxy.edx_grades.forms import EdXGradesForm, ACTIONS
from lmod_proxy.edx_grades.actions import (
    get_assignments,
    get_membership,
    get_sections,
    post_grades,
)
from lmod_proxy.tests.common import CommonTest


class TestEdXGrades(CommonTest):
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
        self.client = self.app.test_client()

    def test_form(self):
        """Verify the form has all the fields as we expect it"""

        with self.app.app_context():
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
            strip_key_list = ('user', 'gradebook', 'section')
            for key in strip_key_list:
                local_form[key] = ' {0} '.format(local_form[key])

            form = EdXGradesForm(**local_form)
            form.validate()

            for key, item in form.data.items():
                self.assertEqual(self.FULL_FORM[key], item)

    @mock.patch('lmod_proxy.edx_grades.log', autospec=True)
    def test_get_root(self, log):
        """Test the GET response returns what we want"""
        headers = self.get_basic_auth_headers()
        headers['X-Forwarded-For'] = ['abc']
        response = self.client.get(
            self.EDX_GRADE_URL,
            headers=headers
        )
        self.assertEqual(200, response.status_code)
        log.info.assert_called_with(
            'edX remote gradebook GET request from %s',
            'abc'
        )

    def test_bad_post(self):
        """Verify we get a json response with an error when we POST bad data"""
        local_form = copy.deepcopy(self.FULL_FORM)
        del local_form['user']

        response = self.client.post(
            self.EDX_GRADE_URL,
            data=local_form,
            headers=self.get_basic_auth_headers()
        )
        self.assertEqual(422, response.status_code)
        self.assertEqual(
            json.loads(response.data),
            {
                'msg': ('Malformed API Call: {\'user\': '
                        '[\'Invalid email address.\']}'),
                'data': [],
            }
        )

    @mock.patch('lmod_proxy.edx_grades.GradeBook', autospec=True)
    def test_post_actions(self, patched_gradebook):
        """Verify that we call the right functions with each action type"""
        local_form = copy.deepcopy(self.FULL_FORM)

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
                    self.EDX_GRADE_URL,
                    data=local_form,
                    headers=self.get_basic_auth_headers()
                )
                self.assertEqual(200, response.status_code)
                self.assertTrue(mock_instrumented_actions[action].called)
                self.assertTrue(patched_gradebook.called)
                self.assertEqual(json.loads(response.data)['data'], ['bar'])

    def test_get_sections(self):
        """Test get_sections actions as expected"""
        with self.app.app_context():
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
        with self.app.app_context():
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
        with self.app.app_context():
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

    @mock.patch('lmod_proxy.edx_grades.actions.log', autospec=True)
    def test_post_grades(self, mock_log):
        """Test post_grades actions as expected"""

        file_form = copy.deepcopy(self.FULL_FORM)
        file_form['datafile'] = FileStorage(
            stream=io.BytesIO(file_form['datafile'].encode('utf8')),
            filename='testfile.csv',
            content_type='text/csv')
        with self.app.app_context():
            form = EdXGradesForm(**file_form)
        gradebook = mock.MagicMock()
        gradebook_return = {'data': {'test': 'foo'}}
        gradebook.spreadsheet2gradebook.return_value = (gradebook_return, 1)

        # Call regularly
        with self.app.app_context():
            message, data, success = post_grades(gradebook, form)
        self.assertTrue(gradebook.spreadsheet2gradebook.called)
        self.assertEqual(data, [])

        # Now raise an expected exception
        self.assertTrue(success)
        gradebook.spreadsheet2gradebook.side_effect = PyLmodException('test')
        with self.app.app_context():
            message, data, success = post_grades(gradebook, form)
        self.assertTrue(gradebook.spreadsheet2gradebook.called)
        self.assertFalse(success)
        self.assertEqual(message, 'test')
        self.assertEqual(data, [])

        # Now fail a few grades
        gradebook_return['data']['numFailures'] = 100
        gradebook_return['data']['results'] = ['completely unexpected']
        gradebook.spreadsheet2gradebook.side_effect = None

        with self.app.app_context():
            with mock.patch(
                    'lmod_proxy.edx_grades.actions.render_template',
                    autospec=True
            ) as mock_template:
                message, data, success = post_grades(gradebook, form)

        self.assertTrue(gradebook.spreadsheet2gradebook.called)
        mock_template.assert_called_with(
            'grade_transfer_failed.html',
            number_failed=100,
            failed_grades=['completely unexpected']
        )
        self.assertFalse(success)
        self.assertEqual(data, [])

    def test_post_grades_approve(self):
        """Validate that approve grades works"""
        file_form = copy.deepcopy(self.FULL_FORM)
        file_form['datafile'] = FileStorage(
            stream=io.BytesIO(file_form['datafile'].encode('utf8')),
            filename='testfile.csv',
            content_type='text/csv')

        with self.app.app_context():
            form = EdXGradesForm(**file_form)
        gradebook = mock.MagicMock()
        gradebook_return = {'data': {'test': 'foo'}}
        gradebook.spreadsheet2gradebook.return_value = (gradebook_return, 1)

        with self.app.app_context():
            with mock.patch.dict(
                'lmod_proxy.edx_grades.actions.current_app.config',
                {'LMODP_APPROVE_GRADES': 'a'}
            ):
                _, data, _ = post_grades(gradebook, form)
        self.assertTrue(gradebook.spreadsheet2gradebook.called)
        self.assertTrue(
            gradebook.spreadsheet2gradebook.call_args[1]['approve_grades']
        )
        self.assertEqual(data, [])

    def test_max_points(self):
        """Validate max points arguments"""
        file_form = copy.deepcopy(self.FULL_FORM)
        file_form['datafile'] = FileStorage(
            stream=io.BytesIO(file_form['datafile'].encode('utf8')),
            filename='testfile.csv',
            content_type='text/csv')

        with self.app.app_context():
            form = EdXGradesForm(**file_form)
            gradebook = mock.MagicMock()
            gradebook_return = {'data': {'test': 'foo'}}
            gradebook.spreadsheet2gradebook.return_value = (
                gradebook_return,
                1
            )

            with mock.patch.dict(
                'lmod_proxy.edx_grades.actions.current_app.config',
                {'LMODP_APPROVE_GRADES': 'a'}
            ):
                _, data, _ = post_grades(gradebook, form)
        assert gradebook.spreadsheet2gradebook.called
        kwargs = gradebook.spreadsheet2gradebook.call_args[1]
        assert kwargs['use_max_points_column']
        assert kwargs['max_points_column'] == 'max_pts'
        assert kwargs['normalize_column'] == 'normalize'

    def test_template_existence(self):
        """Just an OS test that the templates we need exist"""
        template_list = [
            'grade_transfer_failed.html',
            'api_message.html',
            'index.html',
        ]

        for template in template_list:
            edx_grades.open_resource('templates/edx_grades/{0}'.format(
                template
            ))
