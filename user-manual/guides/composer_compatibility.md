# USD Composer Version Compatibility

While Farm can support many forms of batch operation, using it for offline batch processing with USD Composer, such as rendering or geometry conversion, is a very common one. As such, we have created this compatibility guide.

## Kit App Template (KAT) Builds

When deploying applications built from the KAT to Farm installations prior to Farm 2.x, use the version of Farm that corresponds to the version of Kit used to build the application.

  Farm      Kit Version Used with KAT
  --------- ---------------------------------
  2.x       Any, but must be "Fat packaged"
  106.0.x   106.x

  : Farm and KAT Compatibility Matrix

### Farm Dependencies

For easiest results, the following should be added to the `[dependency]` section of your Kit application's `.kit` file:

``` toml
"omni.services.render" = {}
"omni.services.farm.agent.runner" = {}
```

### Fat Packaging

Fat Packaging ensures all required dependencies are included with the application. This is required for Farm 2.x and may also make it possible to run Kit applications on Farm instances with different Kit versions (i.e., Farm 105.x with 106.x Kit based applications).
