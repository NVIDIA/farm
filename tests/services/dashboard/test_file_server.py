# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest import IsolatedAsyncioTestCase
from nv.svc.farm.services.dashboard.server import SinglePageAppWebServer
from nv.svc.core.main import ServicesCore


class TestWebUiFacility(IsolatedAsyncioTestCase):
    """Testing Web UI Facility."""

    def setUp(self):
        self.endpoint = "/app"
        self.version = "0.1.0"
        self.name = "test"
        self.build_sub_directory = None
        self.core = ServicesCore()
        self.client = TestClient(self.core.app)
        self.static_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "build")
        self.index_html_file = self.template_index_html(self.endpoint)
        self.assets_css_file = self._read_file(os.path.join(self.static_directory, "assets", "index.css"))
        self.assets_js_file = self._read_file(os.path.join(self.static_directory, "assets", "index.js"))
        self.static_css_file = self._read_file(os.path.join(self.static_directory, "static", "css", "index.css"))
        self.static_js_file = self._read_file(os.path.join(self.static_directory, "static", "js", "index.js"))
        self.icon_svg_file = self._read_file(os.path.join(self.static_directory, "icon.svg"))

        self.responses = {
            "app": {
                "/config": {
                    "config_value_1": "1",
                    "config_value_2": "2",
                },
                "/version": self.version,
                "errors": {"not_found": '{"detail":"Not Found"}'},
            },
            "api": {
                "/": {"data": "success"},
                "/error": {"detail": "Test error 500", "status_code": 500},
                "/not_found": {"detail": "Test error 404", "status_code": 404},
            },
        }

        self.file_path_tests = [
            # sub path icon file
            ("/app/some/sub/path/icon.svg", self.icon_svg_file),
            ("/app/static/js/index.js", self.static_js_file),
            ("/app/static/css/index.css", self.static_css_file),
            ("/app/assets/index.js", self.assets_js_file),
            ("/app/assets/index.css", self.assets_css_file),
            (
                "/app/e57_store_event-command_runner.handle_nucleus_event-07cc41b3-5db1-4cb3-a3c1-b302da2aca56",
                self.index_html_file,
            ),
            ("/app/index.html", self.index_html_file),
        ]

    def _read_file(self, file_path):
        with open(file_path, "r") as file:
            return file.read()

    def _setup_routes(self):
        web_ui_facility = SinglePageAppWebServer(
            core=self.core,
            service_name=self.name,
            version=self.version,
            frontend_root_path="",
            frontend_host="",
            frontend_url_prefix=f"{self.endpoint}",
            static_directory=self.static_directory,
            build_sub_directory=self.build_sub_directory,
        )

        web_ui_facility.startup()

        for key, value in self.responses["app"]["/config"].items():
            web_ui_facility.add_config_value(key, value)

        @self.core.app.get("/api")
        async def get_api():
            return self.responses["api"]["/"]

        @self.core.app.get("/api/error")
        async def get_api_500():
            raise HTTPException(**self.responses["api"]["/error"])

        @self.core.app.get("/api/not_found")
        async def get_api_404():
            raise HTTPException(**self.responses["api"]["/not_found"])

    def assert_index_html_response(self, response):
        html = response.content.decode("utf-8")
        self.assertEqual(self.index_html_file.strip(), html.strip())
        self.assertEqual(response.headers.get("cache-control"), "no-cache")

    def assert_file_response(self, path: str, file: str):
        response = self.client.get(path)

        if file == self.index_html_file:
            return self.assert_index_html_response(response)

        content = response.content.decode("utf-8")
        self.assertEqual(content, file)

    def assert_file_paths(self, file_path_tests: list[tuple[str, str]]):
        for path, file in file_path_tests:
            self.assert_file_response(path, file)

    def template_index_html(self, base: str):
        return f'<html><head><base href="/{base.strip("/")}/"></head></html>'


class TestBaseCase(TestWebUiFacility):
    def setUp(self):
        super().setUp()
        self._setup_routes()


class TestGetAssetFiles(TestBaseCase):
    def test_fetching_files_base_case(self):
        """Get Files Base Case"""
        file_path_tests = [
            # sub path static js file
            ("/app/some/sub/path/static/js/index.js", self.index_html_file),
            # sub path static css file
            ("/app/some/sub/path/static/css/index.css", self.index_html_file),
            # sub path assets js file
            ("/app/some/sub/path/assets/index.js", self.index_html_file),
            # sub path assets css file
            ("/app/some/sub/path/assets/index.css", self.index_html_file),
        ]

        self.assert_file_paths(file_path_tests + self.file_path_tests)


class TestBuildAssetsSubDirectory(TestWebUiFacility):
    def setUp(self):
        super().setUp()
        self.build_sub_directory = "assets"
        self._setup_routes()

    def test_fetching_files_with_assets_sub_path(self):
        """Get Files form build/assets Sub Directory"""
        file_path_tests = [
            # sub path assets js file
            (f"/app/some/sub/path/{self.build_sub_directory}/index.js", self.assets_js_file),
            # sub path assets css file
            (f"/app/some/sub/path/{self.build_sub_directory}/index.css", self.assets_css_file),
        ]
        self.assert_file_paths(file_path_tests + self.file_path_tests)


class TestBuildStaticSubDirectory(TestWebUiFacility):
    def setUp(self):
        super().setUp()
        self.build_sub_directory = "static"
        self._setup_routes()

    def test_fetching_files_with_static_sub_path(self):
        """Get File From build/static Sub Directory"""
        file_path_tests = [
            # sub path static js file
            (f"/app/some/sub/path/{self.build_sub_directory}/js/index.js", self.static_js_file),
            # sub path static css file
            (f"/app/some/sub/path/{self.build_sub_directory}/css/index.css", self.static_css_file),
        ]
        self.assert_file_paths(file_path_tests + self.file_path_tests)


class TestNoStaticDirectory(TestWebUiFacility):
    def setUp(self):
        super().setUp()
        self.static_directory = ""
        self._setup_routes()

    def test_fetching_files_with_no_static_directory(self):
        """Get File With No Static Directory"""
        file_path_tests = [(test_path, self.responses["app"]["errors"]["not_found"]) for test_path, _ in self.file_path_tests]
        self.assert_file_paths(file_path_tests)


class TestAppRouting(TestBaseCase):
    def test_get_root_route(self):
        """Get root route"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

    def test_get_root_frontend_route(self):
        """Get root frontend route"""
        response = self.client.get("/app")
        self.assert_index_html_response(response)

    def test_get_root_frontend_route_with_terminating_slash(self):
        """Get root frontend route with terminating slash"""
        response = self.client.get("/app/")
        self.assert_index_html_response(response)

    def test_get_assets_404_route(self):
        """Get Request on Unknown Route"""
        response = self.client.get("/app/this/route/does/not/exist")
        self.assert_index_html_response(response)

    def test_get_config(self):
        """Get Config Route"""
        response = self.client.get("/app/config")
        self.assertEqual(response.json(), self.responses["app"]["/config"])

    def test_get_version(self):
        """Get Version Route"""
        response = self.client.get("/app/version")
        self.assertEqual(response.json(), self.responses["app"]["/version"])


class TestApiRouting(TestBaseCase):
    def test_api_get(self):
        """Get Request for Non Frontend Api"""
        response = self.client.get("/api")
        data = response.json()
        self.assertEqual(data, self.responses["api"]["/"])

    def test_api_get_500(self):
        """Get Request 500 Error for Non Frontend Api"""
        response = self.client.get("/api/error")
        data = response.json()
        self.assertEqual(data["detail"], self.responses["api"]["/error"]["detail"])

    def test_api_get_404(self):
        """Get Request 404 Error for Non Frontend Api"""
        response = self.client.get("/api/not_found")
        data = response.json()
        self.assertEqual(data["detail"], self.responses["api"]["/not_found"]["detail"])


class TestDynamicFrontendUrlPrefix(TestWebUiFacility):
    def setUp(self):
        super().setUp()
        self.endpoint = "/queue/management/dashboard/"
        self.index_html_file = self.template_index_html(self.endpoint)
        self._setup_routes()

    def test_dynamic_frontend_url_prefix(self):
        """Get Index HTML With Dynamic URL Prefix"""

        response = self.client.get(self.endpoint)
        self.assert_index_html_response(response)

    def test_forwarded_path(self):
        """Get Index HTML With Forwarded Path"""

        forwarded_path = "/dashboard/"
        response = self.client.get(self.endpoint, headers={"X-Forwarded-Path": forwarded_path})
        self.index_html_file = self.template_index_html(forwarded_path)
        self.assert_index_html_response(response)
