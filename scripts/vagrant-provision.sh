#!/usr/bin/env bash

pushd /vagrant

fab pysetup
fab rdb

popd
