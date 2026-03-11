// ─────────────────────────────────────────────────────────────────────────────
// FILE: network/SeHATApiService.kt
// Retrofit interface for all three SeHAT AI Backend endpoints.
// ─────────────────────────────────────────────────────────────────────────────

package com.sehat.smartcare.network

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface SeHATApiService {

    // ── 1. Symptom Checker ────────────────────────────────────────────────────
    @POST("symptom-check")
    suspend fun checkSymptoms(
        @Body request: SymptomRequest
    ): Response<SymptomResponse>

    // ── 2. Medical Report Analyzer ────────────────────────────────────────────
    @POST("analyze-report")
    suspend fun analyzeReport(
        @Body request: ReportRequest
    ): Response<ReportResponse>

    // ── 3. Medical Chatbot ────────────────────────────────────────────────────
    @POST("medical-chat")
    suspend fun medicalChat(
        @Body request: ChatRequest
    ): Response<ChatResponse>
}
