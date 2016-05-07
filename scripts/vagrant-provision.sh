#!/usr/bin/env bash

echo "export PORT=8000" >> ~/.bashrc

pushd /vagrant

fab pysetup

popd
