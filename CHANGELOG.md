## [1.1.3](https://github.com/NVIDIA/farm/compare/1.1.2...1.1.3) (2026-02-09)

### 🐛 Bug Fixes 🐛

* helm push path ([#15](https://github.com/NVIDIA/farm/issues/15)) ([4188d5b](https://github.com/NVIDIA/farm/commit/4188d5b7555e98ecda7365746b38a4df0c5c4ebd))

## [1.1.2](https://github.com/NVIDIA/farm/compare/1.1.1...1.1.2) (2026-02-09)

### 🐛 Bug Fixes 🐛

* release permissions for helm push ([#14](https://github.com/NVIDIA/farm/issues/14)) ([f270d87](https://github.com/NVIDIA/farm/commit/f270d876a7cb6b8ee8c8240850e8893db5aa5f5f))

## [1.1.1](https://github.com/NVIDIA/farm/compare/1.1.0...1.1.1) (2026-02-06)

### 🐛 Bug Fixes 🐛

* inconsistent enum string synthesis ([#13](https://github.com/NVIDIA/farm/issues/13)) ([5da9033](https://github.com/NVIDIA/farm/commit/5da903335ba58fe822e363387d0b2a9bc1bd0fac))

### 📝 Documentation 📝

* update github action workflow readme ([#12](https://github.com/NVIDIA/farm/issues/12)) ([d7fe08a](https://github.com/NVIDIA/farm/commit/d7fe08a0860eba30e0575870e7178d5291bedf29))

## [1.1.0](https://github.com/NVIDIA/farm/compare/1.0.1...1.1.0) (2026-02-05)

### ✨ Features ✨

* add e2e tests and fix docker artifact passing ([#11](https://github.com/NVIDIA/farm/issues/11)) ([e59a289](https://github.com/NVIDIA/farm/commit/e59a2891e0e7855828bef89a2f552fd7bbebb642))

### 🛠 CI Improvements 🛠

* complete ci refactor for dependencies and proper workflows ([#10](https://github.com/NVIDIA/farm/issues/10)) ([11f273d](https://github.com/NVIDIA/farm/commit/11f273d0802ab87f69e64135754161ebee243be0))

## [1.0.1](https://github.com/NVIDIA/farm/compare/1.0.0...1.0.1) (2026-01-29)

### 🐛 Bug Fixes 🐛

* remove nv logo ([#8](https://github.com/NVIDIA/farm/issues/8)) ([89e3530](https://github.com/NVIDIA/farm/commit/89e35308e09e9f8269a1bb9a98ac3b14517ab431))

## 1.0.0 (2026-01-28)

### ✨ Features ✨

* add Helm chart and CI pipeline for chart publishing ([#4](https://github.com/NVIDIA/farm/issues/4)) ([add0719](https://github.com/NVIDIA/farm/commit/add07190cd610d8db0effba2e7998ef6b8ad45cc))

### 🐛 Bug Fixes 🐛

* broken status transition exception text check ([ceeb1ca](https://github.com/NVIDIA/farm/commit/ceeb1ca37cb0dede1133d16dff0270213acac2b3))
* force ipv4 to avoid ipv6 host bind failures ([a39b1a7](https://github.com/NVIDIA/farm/commit/a39b1a7c1d71b89a7e4fbdaad145c5ddeda11de8))
* move python run image to the same as the builder to fix python version mismatches ([cfc79a2](https://github.com/NVIDIA/farm/commit/cfc79a2c12529e3f74568cae569eefff023c0eef))

### Chores

* **release:** 1.0.0 - nv.svc.farm ([95bd7a9](https://github.com/NVIDIA/farm/commit/95bd7a9e242fc0258a0cd90ab7109660680db326)), closes [#4](https://github.com/NVIDIA/farm/issues/4) [#3](https://github.com/NVIDIA/farm/issues/3) [#5](https://github.com/NVIDIA/farm/issues/5)
* add dashboard ([4694ced](https://github.com/NVIDIA/farm/commit/4694ceda84fd35e9564c7ebfeed08ba6758c341e))
* scrub more internal names ([b4b38f0](https://github.com/NVIDIA/farm/commit/b4b38f0dd1ca65b0791884fba9963b8e1983fa99))
* update poetry deps ([bed42db](https://github.com/NVIDIA/farm/commit/bed42db7ec72cdff9e6d77485598a9baecf6d123))

### 🛠 CI Improvements 🛠

* add GitHub Actions workflows and update Python to 3.12 ([#3](https://github.com/NVIDIA/farm/issues/3)) ([476ca6b](https://github.com/NVIDIA/farm/commit/476ca6bf487aff533f1413f13e96df2216cb8b27))
* fix for semantic release, only run tests on changes ([#5](https://github.com/NVIDIA/farm/issues/5)) ([c5ee7b3](https://github.com/NVIDIA/farm/commit/c5ee7b32d53f849ac71db0600fccdcb7d1dd8d3c))
* fix release for github ([#6](https://github.com/NVIDIA/farm/issues/6)) ([4c985e8](https://github.com/NVIDIA/farm/commit/4c985e8d269da4ff8ebe270aef1a131d04aaefe7))

## 1.0.0 (2026-01-28)

### ✨ Features ✨

* add Helm chart and CI pipeline for chart publishing ([#4](https://github.com/NVIDIA/farm/issues/4)) ([add0719](https://github.com/NVIDIA/farm/commit/add07190cd610d8db0effba2e7998ef6b8ad45cc))

### 🐛 Bug Fixes 🐛

* broken status transition exception text check ([ceeb1ca](https://github.com/NVIDIA/farm/commit/ceeb1ca37cb0dede1133d16dff0270213acac2b3))
* force ipv4 to avoid ipv6 host bind failures ([a39b1a7](https://github.com/NVIDIA/farm/commit/a39b1a7c1d71b89a7e4fbdaad145c5ddeda11de8))
* move python run image to the same as the builder to fix python version mismatches ([cfc79a2](https://github.com/NVIDIA/farm/commit/cfc79a2c12529e3f74568cae569eefff023c0eef))

### Chores

* add dashboard ([4694ced](https://github.com/NVIDIA/farm/commit/4694ceda84fd35e9564c7ebfeed08ba6758c341e))
* scrub more internal names ([b4b38f0](https://github.com/NVIDIA/farm/commit/b4b38f0dd1ca65b0791884fba9963b8e1983fa99))
* update poetry deps ([bed42db](https://github.com/NVIDIA/farm/commit/bed42db7ec72cdff9e6d77485598a9baecf6d123))

### 🛠 CI Improvements 🛠

* add GitHub Actions workflows and update Python to 3.12 ([#3](https://github.com/NVIDIA/farm/issues/3)) ([476ca6b](https://github.com/NVIDIA/farm/commit/476ca6bf487aff533f1413f13e96df2216cb8b27))
* fix for semantic release, only run tests on changes ([#5](https://github.com/NVIDIA/farm/issues/5)) ([c5ee7b3](https://github.com/NVIDIA/farm/commit/c5ee7b32d53f849ac71db0600fccdcb7d1dd8d3c))
