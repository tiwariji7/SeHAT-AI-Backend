// ─────────────────────────────────────────────────────────────────────────────
// FILE: network/ApiModels.kt
// Data classes for every request and response.
// ─────────────────────────────────────────────────────────────────────────────

package com.sehat.smartcare.network

import com.google.gson.annotations.SerializedName

// ── Symptom Checker ──────────────────────────────────────────────────────────

data class SymptomRequest(
    val symptoms: String
)

data class SymptomResponse(
    val conditions: List<ConditionResult>,
    val summary: String
)

data class ConditionResult(
    val disease: String,
    val confidence: Int
)

// ── Medical Report Analyzer ──────────────────────────────────────────────────

data class PatientInfo(
    val name: String,
    val age: Int,
    val gender: String
)

data class LabParameter(
    val name: String,
    val value: String,
    val references: String
)

data class ReportInfo(
    @SerializedName("report_name") val reportName: String,
    val parameters: List<LabParameter>
)

data class ReportRequest(
    @SerializedName("patient_info") val patientInfo: PatientInfo,
    @SerializedName("report_info") val reportInfo: ReportInfo
)

data class AbnormalParameter(
    val name: String,
    val value: Double,
    val status: String,       // "Low" or "High"
    val reference: String
)

data class ReportResponse(
    @SerializedName("abnormal_parameters") val abnormalParameters: List<AbnormalParameter>,
    @SerializedName("english_summary") val englishSummary: String,
    @SerializedName("hindi_summary") val hindiSummary: String
)

// ── Medical Chatbot ──────────────────────────────────────────────────────────

data class ChatRequest(
    val message: String
)

data class ChatResponse(
    val response: String
)
