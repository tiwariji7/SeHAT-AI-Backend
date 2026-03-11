// ─────────────────────────────────────────────────────────────────────────────
// FILE: network/RetrofitClient.kt
// Singleton Retrofit instance — swap BASE_URL with your Render URL after deploy.
// ─────────────────────────────────────────────────────────────────────────────

package com.sehat.smartcare.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    // ── Replace with your Render URL after deploying ──────────────────────────
    private const val BASE_URL = "https://sehat-ai-backend.onrender.com/"
    // ─────────────────────────────────────────────────────────────────────────

    private val logging = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(logging)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)   // LLM can take up to ~90 s
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    val api: SeHATApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(SeHATApiService::class.java)
    }
}
