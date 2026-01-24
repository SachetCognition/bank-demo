/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import { fetchBaseQuery, createApi } from "@reduxjs/toolkit/query/react";
import ApiUrls from "./apiUrls";

const usersUrl = import.meta.env.VITE_USERS_URL || ApiUrls.VITE_USERS_URL;

const baseQuery = fetchBaseQuery({ 
  baseUrl: "",
  credentials: 'include',
});

export const apiSlice = createApi({
  baseQuery,
  tagTypes: ["User"],
  endpoints: () => ({}),
});

export const userApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (data) => ({
        url: `${usersUrl}/auth`,
        method: "POST",
        body: data,
      }),
    }),
    logout: builder.mutation({
      query: () => ({
        url: `${usersUrl}/logout`,
        method: "POST",
      }),
    }),
    register: builder.mutation({
      query: (data) => ({
        url: `${usersUrl}`,
        method: "POST",
        body: data,
      }),
    }),
    updateUser: builder.mutation({
      query: (data) => ({
        url: `${usersUrl}/profile`,
        method: "PUT",
        body: data,
      }),
    }),
    checkAuth: builder.query({
      query: () => ({
        url: `${usersUrl}/check-auth`,
        method: "GET",
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useLogoutMutation,
  useRegisterMutation,
  useUpdateUserMutation,
  useCheckAuthQuery,
} = userApiSlice;
