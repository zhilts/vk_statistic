# vk-fetch

## DEV-env Setup

To create dev env run `vagrant up` from the project root

## Run server

```shell
fab manage:"runserver 0.0.0.0:8000"
```

## Recreate Database

```shell
fab rdb
```

## Start Bidding
```shell
fab manage:start_fetching
```