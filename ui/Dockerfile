# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

FROM --platform=linux/amd64 node:22-alpine
WORKDIR /bankapp
EXPOSE 3000
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps --silent
COPY . ./
CMD ["npm", "run", "ui"]
