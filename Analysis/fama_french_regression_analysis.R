# =============================================================================
# FAMA-FRENCH FACTOR ANALYSIS: REGRESSION MODELS FOR ITALIAN FTSE MIB STOCKS
# =============================================================================

library(readxl)

# -----------------------------------------------------------------------------
# 1. DATA LOADING AND PREPARATION
# -----------------------------------------------------------------------------

data <- read_excel("C:/Users/ricca/Desktop/FrenchFamaOnlyTable.xlsx")

# Remove market aggregate row
data <- data[data$Dimensions != "/" & !is.na(data$Sector), ]

# Clean column names
colnames(data) <- gsub(" ", "_", colnames(data))
colnames(data) <- gsub("-", "_", colnames(data))

# Convert "/" to NA for Nexi's missing return
data$AVG_Return__2015_2019[data$AVG_Return__2015_2019 == "/"] <- NA
data$AVG_Return__2015_2019 <- as.numeric(data$AVG_Return__2015_2019)

# Create factor variables
data$Dimensions <- factor(data$Dimensions, levels = c("Small", "Medium", "Large"))
data$Sector <- factor(data$Sector)

# Rename key variables for easier use
names(data)[names(data) == "Beta_(Last_5y,_monthly)"] <- "Beta"
names(data)[names(data) == "AVG_Return__2015_2019"] <- "Return_15_19"
names(data)[names(data) == "AVG_Return_2020_2024"] <- "Return_20_24"
names(data)[names(data) == "AVG_Return_2015_2024"] <- "Return_15_24"
names(data)[names(data) == "AVG_PE_2015_2019"] <- "PE_15_19"
names(data)[names(data) == "AVG_PE_2020_2024"] <- "PE_20_24"
names(data)[names(data) == "AVG_PE_2015_2024"] <- "PE_15_24"
names(data)[names(data) == "TA/MKTCAP_2015_2019"] <- "TA_MKTCAP_15_19"
names(data)[names(data) == "TA/MKTCAP_2020_2024"] <- "TA_MKTCAP_20_24"
names(data)[names(data) == "TA/MKTCAP_2015_2024"] <- "TA_MKTCAP_15_24"
names(data)[names(data) == "TA/BE_2015___2019"] <- "TA_BE_15_19"
names(data)[names(data) == "TA/BE_2020___2024"] <- "TA_BE_20_24"
names(data)[names(data) == "TA/BE_2015_2024"] <- "TA_BE_15_24"
names(data)[names(data) == "BE/MKTCAP_2015___2019"] <- "BE_MKTCAP_15_19"
names(data)[names(data) == "BE/MKTCAP_2020_2024"] <- "BE_MKTCAP_20_24"
names(data)[names(data) == "BE/MKTCAP_2015_2024"] <- "BE_MKTCAP_15_24"

cat("========================================================================\n")
cat("FAMA-FRENCH REGRESSION ANALYSIS - ITALIAN FTSE MIB STOCKS\n")
cat("========================================================================\n\n")

cat("Dataset: n =", nrow(data), "companies\n")
cat("Sectors:", levels(data$Sector), "\n")
cat("Dimensions:", levels(data$Dimensions), "\n\n")


# =============================================================================
# 2. PERIOD 2015-2019 REGRESSIONS
# =============================================================================

cat("\n########################################################################\n")
cat("PERIOD 2015-2019 ANALYSIS\n")
cat("########################################################################\n\n")

# Subset data with valid returns for 2015-2019
data_15_19 <- data[!is.na(data$Return_15_19), ]
cat("Valid observations for 2015-2019:", nrow(data_15_19), "\n\n")

# --- Model 1: CAPM (Return vs Beta only) ---
cat("--- Model 1: CAPM (Return ~ Beta) ---\n")
m1_15_19 <- lm(Return_15_19 ~ Beta, data = data_15_19)
print(summary(m1_15_19))

# --- Model 2: Return vs PE ---
cat("\n--- Model 2: Return ~ PE Ratio ---\n")
m2_15_19 <- lm(Return_15_19 ~ PE_15_19, data = data_15_19)
print(summary(m2_15_19))

# --- Model 3: Return vs Size (BE/MKTCAP) ---
cat("\n--- Model 3: Return ~ BE/MKTCAP (Book-to-Market) ---\n")
m3_15_19 <- lm(Return_15_19 ~ BE_MKTCAP_15_19, data = data_15_19)
print(summary(m3_15_19))

# --- Model 4: Return vs TA/MKTCAP ---
cat("\n--- Model 4: Return ~ TA/MKTCAP ---\n")
m4_15_19 <- lm(Return_15_19 ~ TA_MKTCAP_15_19, data = data_15_19)
print(summary(m4_15_19))

# --- Model 5: Return vs TA/BE (Leverage proxy) ---
cat("\n--- Model 5: Return ~ TA/BE ---\n")
m5_15_19 <- lm(Return_15_19 ~ TA_BE_15_19, data = data_15_19)
print(summary(m5_15_19))

# --- Model 6: Return vs Size (Dimensions categorical) ---
cat("\n--- Model 6: Return ~ Dimensions (Size Category) ---\n")
m6_15_19 <- lm(Return_15_19 ~ Dimensions, data = data_15_19)
print(summary(m6_15_19))

# --- Model 7: Return vs Sector ---
cat("\n--- Model 7: Return ~ Sector ---\n")
m7_15_19 <- lm(Return_15_19 ~ Sector, data = data_15_19)
print(summary(m7_15_19))

# --- Model 8: Beta + PE ---
cat("\n--- Model 8: Return ~ Beta + PE ---\n")
m8_15_19 <- lm(Return_15_19 ~ Beta + PE_15_19, data = data_15_19)
print(summary(m8_15_19))

# --- Model 9: Beta + BE/MKTCAP (Fama-French style) ---
cat("\n--- Model 9: Return ~ Beta + BE/MKTCAP ---\n")
m9_15_19 <- lm(Return_15_19 ~ Beta + BE_MKTCAP_15_19, data = data_15_19)
print(summary(m9_15_19))

# --- Model 10: Beta + Dimensions ---
cat("\n--- Model 10: Return ~ Beta + Dimensions ---\n")
m10_15_19 <- lm(Return_15_19 ~ Beta + Dimensions, data = data_15_19)
print(summary(m10_15_19))

# --- Model 11: Beta + Sector ---
cat("\n--- Model 11: Return ~ Beta + Sector ---\n")
m11_15_19 <- lm(Return_15_19 ~ Beta + Sector, data = data_15_19)
print(summary(m11_15_19))

# --- Model 12: Full model with all continuous variables ---
cat("\n--- Model 12: Full Continuous Model ---\n")
cat("Return ~ Beta + PE + TA/MKTCAP + TA/BE + BE/MKTCAP\n")
m12_15_19 <- lm(Return_15_19 ~ Beta + PE_15_19 + TA_MKTCAP_15_19 + 
                  TA_BE_15_19 + BE_MKTCAP_15_19, data = data_15_19)
print(summary(m12_15_19))

# --- Model 13: Full model with categorical variables ---
cat("\n--- Model 13: Full Model with Categories ---\n")
cat("Return ~ Beta + PE + BE/MKTCAP + Dimensions + Sector\n")
m13_15_19 <- lm(Return_15_19 ~ Beta + PE_15_19 + BE_MKTCAP_15_19 + 
                  Dimensions + Sector, data = data_15_19)
print(summary(m13_15_19))

# --- Model 14: Kitchen sink model ---
cat("\n--- Model 14: Kitchen Sink Model (All Variables) ---\n")
m14_15_19 <- lm(Return_15_19 ~ Beta + PE_15_19 + TA_MKTCAP_15_19 + 
                  TA_BE_15_19 + BE_MKTCAP_15_19 + Dimensions + Sector, 
                data = data_15_19)
print(summary(m14_15_19))


# =============================================================================
# 3. PERIOD 2020-2024 REGRESSIONS
# =============================================================================

cat("\n########################################################################\n")
cat("PERIOD 2020-2024 ANALYSIS\n")
cat("########################################################################\n\n")

data_20_24 <- data
cat("Valid observations for 2020-2024:", nrow(data_20_24), "\n\n")

# --- Model 1: CAPM ---
cat("--- Model 1: CAPM (Return ~ Beta) ---\n")
m1_20_24 <- lm(Return_20_24 ~ Beta, data = data_20_24)
print(summary(m1_20_24))

# --- Model 2: Return vs PE ---
cat("\n--- Model 2: Return ~ PE Ratio ---\n")
m2_20_24 <- lm(Return_20_24 ~ PE_20_24, data = data_20_24)
print(summary(m2_20_24))

# --- Model 3: Return vs BE/MKTCAP ---
cat("\n--- Model 3: Return ~ BE/MKTCAP (Book-to-Market) ---\n")
m3_20_24 <- lm(Return_20_24 ~ BE_MKTCAP_20_24, data = data_20_24)
print(summary(m3_20_24))

# --- Model 4: Return vs TA/MKTCAP ---
cat("\n--- Model 4: Return ~ TA/MKTCAP ---\n")
m4_20_24 <- lm(Return_20_24 ~ TA_MKTCAP_20_24, data = data_20_24)
print(summary(m4_20_24))

# --- Model 5: Return vs TA/BE ---
cat("\n--- Model 5: Return ~ TA/BE ---\n")
m5_20_24 <- lm(Return_20_24 ~ TA_BE_20_24, data = data_20_24)
print(summary(m5_20_24))

# --- Model 6: Return vs Dimensions ---
cat("\n--- Model 6: Return ~ Dimensions (Size Category) ---\n")
m6_20_24 <- lm(Return_20_24 ~ Dimensions, data = data_20_24)
print(summary(m6_20_24))

# --- Model 7: Return vs Sector ---
cat("\n--- Model 7: Return ~ Sector ---\n")
m7_20_24 <- lm(Return_20_24 ~ Sector, data = data_20_24)
print(summary(m7_20_24))

# --- Model 8: Beta + PE ---
cat("\n--- Model 8: Return ~ Beta + PE ---\n")
m8_20_24 <- lm(Return_20_24 ~ Beta + PE_20_24, data = data_20_24)
print(summary(m8_20_24))

# --- Model 9: Beta + BE/MKTCAP ---
cat("\n--- Model 9: Return ~ Beta + BE/MKTCAP ---\n")
m9_20_24 <- lm(Return_20_24 ~ Beta + BE_MKTCAP_20_24, data = data_20_24)
print(summary(m9_20_24))

# --- Model 10: Beta + Dimensions ---
cat("\n--- Model 10: Return ~ Beta + Dimensions ---\n")
m10_20_24 <- lm(Return_20_24 ~ Beta + Dimensions, data = data_20_24)
print(summary(m10_20_24))

# --- Model 11: Beta + Sector ---
cat("\n--- Model 11: Return ~ Beta + Sector ---\n")
m11_20_24 <- lm(Return_20_24 ~ Beta + Sector, data = data_20_24)
print(summary(m11_20_24))

# --- Model 12: Full Continuous ---
cat("\n--- Model 12: Full Continuous Model ---\n")
m12_20_24 <- lm(Return_20_24 ~ Beta + PE_20_24 + TA_MKTCAP_20_24 + 
                  TA_BE_20_24 + BE_MKTCAP_20_24, data = data_20_24)
print(summary(m12_20_24))

# --- Model 13: Full with Categories ---
cat("\n--- Model 13: Full Model with Categories ---\n")
m13_20_24 <- lm(Return_20_24 ~ Beta + PE_20_24 + BE_MKTCAP_20_24 + 
                  Dimensions + Sector, data = data_20_24)
print(summary(m13_20_24))

# --- Model 14: Kitchen Sink ---
cat("\n--- Model 14: Kitchen Sink Model (All Variables) ---\n")
m14_20_24 <- lm(Return_20_24 ~ Beta + PE_20_24 + TA_MKTCAP_20_24 + 
                  TA_BE_20_24 + BE_MKTCAP_20_24 + Dimensions + Sector, 
                data = data_20_24)
print(summary(m14_20_24))


# =============================================================================
# 4. PERIOD 2015-2024 REGRESSIONS (FULL PERIOD)
# =============================================================================

cat("\n########################################################################\n")
cat("PERIOD 2015-2024 ANALYSIS (FULL PERIOD)\n")
cat("########################################################################\n\n")

data_15_24 <- data
cat("Valid observations for 2015-2024:", nrow(data_15_24), "\n\n")

# --- Model 1: CAPM ---
cat("--- Model 1: CAPM (Return ~ Beta) ---\n")
m1_15_24 <- lm(Return_15_24 ~ Beta, data = data_15_24)
print(summary(m1_15_24))

# --- Model 2: Return vs PE ---
cat("\n--- Model 2: Return ~ PE Ratio ---\n")
m2_15_24 <- lm(Return_15_24 ~ PE_15_24, data = data_15_24)
print(summary(m2_15_24))

# --- Model 3: Return vs BE/MKTCAP ---
cat("\n--- Model 3: Return ~ BE/MKTCAP (Book-to-Market) ---\n")
m3_15_24 <- lm(Return_15_24 ~ BE_MKTCAP_15_24, data = data_15_24)
print(summary(m3_15_24))

# --- Model 4: Return vs TA/MKTCAP ---
cat("\n--- Model 4: Return ~ TA/MKTCAP ---\n")
m4_15_24 <- lm(Return_15_24 ~ TA_MKTCAP_15_24, data = data_15_24)
print(summary(m4_15_24))

# --- Model 5: Return vs TA/BE ---
cat("\n--- Model 5: Return ~ TA/BE ---\n")
m5_15_24 <- lm(Return_15_24 ~ TA_BE_15_24, data = data_15_24)
print(summary(m5_15_24))

# --- Model 6: Return vs Dimensions ---
cat("\n--- Model 6: Return ~ Dimensions (Size Category) ---\n")
m6_15_24 <- lm(Return_15_24 ~ Dimensions, data = data_15_24)
print(summary(m6_15_24))

# --- Model 7: Return vs Sector ---
cat("\n--- Model 7: Return ~ Sector ---\n")
m7_15_24 <- lm(Return_15_24 ~ Sector, data = data_15_24)
print(summary(m7_15_24))

# --- Model 8: Beta + PE ---
cat("\n--- Model 8: Return ~ Beta + PE ---\n")
m8_15_24 <- lm(Return_15_24 ~ Beta + PE_15_24, data = data_15_24)
print(summary(m8_15_24))

# --- Model 9: Beta + BE/MKTCAP ---
cat("\n--- Model 9: Return ~ Beta + BE/MKTCAP ---\n")
m9_15_24 <- lm(Return_15_24 ~ Beta + BE_MKTCAP_15_24, data = data_15_24)
print(summary(m9_15_24))

# --- Model 10: Beta + Dimensions ---
cat("\n--- Model 10: Return ~ Beta + Dimensions ---\n")
m10_15_24 <- lm(Return_15_24 ~ Beta + Dimensions, data = data_15_24)
print(summary(m10_15_24))

# --- Model 11: Beta + Sector ---
cat("\n--- Model 11: Return ~ Beta + Sector ---\n")
m11_15_24 <- lm(Return_15_24 ~ Beta + Sector, data = data_15_24)
print(summary(m11_15_24))

# --- Model 12: Full Continuous ---
cat("\n--- Model 12: Full Continuous Model ---\n")
m12_15_24 <- lm(Return_15_24 ~ Beta + PE_15_24 + TA_MKTCAP_15_24 + 
                  TA_BE_15_24 + BE_MKTCAP_15_24, data = data_15_24)
print(summary(m12_15_24))

# --- Model 13: Full with Categories ---
cat("\n--- Model 13: Full Model with Categories ---\n")
m13_15_24 <- lm(Return_15_24 ~ Beta + PE_15_24 + BE_MKTCAP_15_24 + 
                  Dimensions + Sector, data = data_15_24)
print(summary(m13_15_24))

# --- Model 14: Kitchen Sink ---
cat("\n--- Model 14: Kitchen Sink Model (All Variables) ---\n")
m14_15_24 <- lm(Return_15_24 ~ Beta + PE_15_24 + TA_MKTCAP_15_24 + 
                  TA_BE_15_24 + BE_MKTCAP_15_24 + Dimensions + Sector, 
                data = data_15_24)
print(summary(m14_15_24))


# =============================================================================
# 5. PERIOD COMPARISON: 2015-2019 vs 2020-2024
# =============================================================================

cat("\n########################################################################\n")
cat("PERIOD COMPARISON ANALYSIS: 2015-2019 vs 2020-2024\n")
cat("########################################################################\n\n")

cat("=== CAPM (Beta only) Comparison ===\n")
cat("\n2015-2019: Beta coefficient =", round(coef(m1_15_19)["Beta"], 4),
    ", p-value =", round(summary(m1_15_19)$coefficients["Beta", "Pr(>|t|)"], 4),
    ", R² =", round(summary(m1_15_19)$r.squared, 4), "\n")
cat("2020-2024: Beta coefficient =", round(coef(m1_20_24)["Beta"], 4),
    ", p-value =", round(summary(m1_20_24)$coefficients["Beta", "Pr(>|t|)"], 4),
    ", R² =", round(summary(m1_20_24)$r.squared, 4), "\n")

cat("\n=== PE Ratio Comparison ===\n")
cat("2015-2019: PE coefficient =", round(coef(m2_15_19)["PE_15_19"], 6),
    ", p-value =", round(summary(m2_15_19)$coefficients["PE_15_19", "Pr(>|t|)"], 4),
    ", R² =", round(summary(m2_15_19)$r.squared, 4), "\n")
cat("2020-2024: PE coefficient =", round(coef(m2_20_24)["PE_20_24"], 6),
    ", p-value =", round(summary(m2_20_24)$coefficients["PE_20_24", "Pr(>|t|)"], 4),
    ", R² =", round(summary(m2_20_24)$r.squared, 4), "\n")

cat("\n=== BE/MKTCAP (Book-to-Market) Comparison ===\n")
cat("2015-2019: BE/MKTCAP coefficient =", round(coef(m3_15_19)["BE_MKTCAP_15_19"], 4),
    ", p-value =", round(summary(m3_15_19)$coefficients["BE_MKTCAP_15_19", "Pr(>|t|)"], 4),
    ", R² =", round(summary(m3_15_19)$r.squared, 4), "\n")
cat("2020-2024: BE/MKTCAP coefficient =", round(coef(m3_20_24)["BE_MKTCAP_20_24"], 4),
    ", p-value =", round(summary(m3_20_24)$coefficients["BE_MKTCAP_20_24", "Pr(>|t|)"], 4),
    ", R² =", round(summary(m3_20_24)$r.squared, 4), "\n")


# =============================================================================
# 6. SUMMARY TABLE: KEY COEFFICIENTS ACROSS PERIODS
# =============================================================================

cat("\n########################################################################\n")
cat("SUMMARY TABLE: KEY COEFFICIENTS AND SIGNIFICANCE\n")
cat("########################################################################\n\n")

extract_stats <- function(model, var_name) {
  coef_val <- coef(model)[var_name]
  se_val <- summary(model)$coefficients[var_name, "Std. Error"]
  t_val <- summary(model)$coefficients[var_name, "t value"]
  p_val <- summary(model)$coefficients[var_name, "Pr(>|t|)"]
  sig <- ifelse(p_val < 0.01, "***", ifelse(p_val < 0.05, "**", ifelse(p_val < 0.1, "*", "")))
  return(c(round(coef_val, 4), round(se_val, 4), round(t_val, 2), round(p_val, 4), sig))
}

cat("Key: *** p<0.01, ** p<0.05, * p<0.1\n\n")

cat("VARIABLE              | PERIOD    | Coefficient | Std.Error | t-value | p-value | Sig\n")
cat("----------------------|-----------|-------------|-----------|---------|---------|----\n")

# Beta
stats <- extract_stats(m1_15_19, "Beta")
cat(sprintf("Beta (CAPM)           | 2015-2019 | %11.4f | %9.4f | %7.2f | %7.4f | %s\n", 
            as.numeric(stats[1]), as.numeric(stats[2]), as.numeric(stats[3]), as.numeric(stats[4]), stats[5]))
stats <- extract_stats(m1_20_24, "Beta")
cat(sprintf("Beta (CAPM)           | 2020-2024 | %11.4f | %9.4f | %7.2f | %7.4f | %s\n", 
            as.numeric(stats[1]), as.numeric(stats[2]), as.numeric(stats[3]), as.numeric(stats[4]), stats[5]))
stats <- extract_stats(m1_15_24, "Beta")
cat(sprintf("Beta (CAPM)           | 2015-2024 | %11.4f | %9.4f | %7.2f | %7.4f | %s\n", 
            as.numeric(stats[1]), as.numeric(stats[2]), as.numeric(stats[3]), as.numeric(stats[4]), stats[5]))

cat("----------------------|-----------|-------------|-----------|---------|---------|----\n")

# BE/MKTCAP
stats <- extract_stats(m3_15_19, "BE_MKTCAP_15_19")
cat(sprintf("BE/MKTCAP             | 2015-2019 | %11.4f | %9.4f | %7.2f | %7.4f | %s\n", 
            as.numeric(stats[1]), as.numeric(stats[2]), as.numeric(stats[3]), as.numeric(stats[4]), stats[5]))
stats <- extract_stats(m3_20_24, "BE_MKTCAP_20_24")
cat(sprintf("BE/MKTCAP             | 2020-2024 | %11.4f | %9.4f | %7.2f | %7.4f | %s\n", 
            as.numeric(stats[1]), as.numeric(stats[2]), as.numeric(stats[3]), as.numeric(stats[4]), stats[5]))
stats <- extract_stats(m3_15_24, "BE_MKTCAP_15_24")
cat(sprintf("BE/MKTCAP             | 2015-2024 | %11.4f | %9.4f | %7.2f | %7.4f | %s\n", 
            as.numeric(stats[1]), as.numeric(stats[2]), as.numeric(stats[3]), as.numeric(stats[4]), stats[5]))


# =============================================================================
# 7. MODEL FIT COMPARISON (Adjusted R²)
# =============================================================================

cat("\n########################################################################\n")
cat("MODEL FIT COMPARISON (Adjusted R²)\n")
cat("########################################################################\n\n")

cat("MODEL                              | 2015-2019 | 2020-2024 | 2015-2024\n")
cat("-----------------------------------|-----------|-----------|----------\n")

cat(sprintf("M1:  Beta only (CAPM)              | %9.4f | %9.4f | %9.4f\n",
            summary(m1_15_19)$adj.r.squared, summary(m1_20_24)$adj.r.squared, summary(m1_15_24)$adj.r.squared))
cat(sprintf("M2:  PE Ratio                      | %9.4f | %9.4f | %9.4f\n",
            summary(m2_15_19)$adj.r.squared, summary(m2_20_24)$adj.r.squared, summary(m2_15_24)$adj.r.squared))
cat(sprintf("M3:  BE/MKTCAP                     | %9.4f | %9.4f | %9.4f\n",
            summary(m3_15_19)$adj.r.squared, summary(m3_20_24)$adj.r.squared, summary(m3_15_24)$adj.r.squared))
cat(sprintf("M4:  TA/MKTCAP                     | %9.4f | %9.4f | %9.4f\n",
            summary(m4_15_19)$adj.r.squared, summary(m4_20_24)$adj.r.squared, summary(m4_15_24)$adj.r.squared))
cat(sprintf("M5:  TA/BE                         | %9.4f | %9.4f | %9.4f\n",
            summary(m5_15_19)$adj.r.squared, summary(m5_20_24)$adj.r.squared, summary(m5_15_24)$adj.r.squared))
cat(sprintf("M6:  Dimensions                    | %9.4f | %9.4f | %9.4f\n",
            summary(m6_15_19)$adj.r.squared, summary(m6_20_24)$adj.r.squared, summary(m6_15_24)$adj.r.squared))
cat(sprintf("M7:  Sector                        | %9.4f | %9.4f | %9.4f\n",
            summary(m7_15_19)$adj.r.squared, summary(m7_20_24)$adj.r.squared, summary(m7_15_24)$adj.r.squared))
cat(sprintf("M8:  Beta + PE                     | %9.4f | %9.4f | %9.4f\n",
            summary(m8_15_19)$adj.r.squared, summary(m8_20_24)$adj.r.squared, summary(m8_15_24)$adj.r.squared))
cat(sprintf("M9:  Beta + BE/MKTCAP              | %9.4f | %9.4f | %9.4f\n",
            summary(m9_15_19)$adj.r.squared, summary(m9_20_24)$adj.r.squared, summary(m9_15_24)$adj.r.squared))
cat(sprintf("M10: Beta + Dimensions             | %9.4f | %9.4f | %9.4f\n",
            summary(m10_15_19)$adj.r.squared, summary(m10_20_24)$adj.r.squared, summary(m10_15_24)$adj.r.squared))
cat(sprintf("M11: Beta + Sector                 | %9.4f | %9.4f | %9.4f\n",
            summary(m11_15_19)$adj.r.squared, summary(m11_20_24)$adj.r.squared, summary(m11_15_24)$adj.r.squared))
cat(sprintf("M12: All continuous                | %9.4f | %9.4f | %9.4f\n",
            summary(m12_15_19)$adj.r.squared, summary(m12_20_24)$adj.r.squared, summary(m12_15_24)$adj.r.squared))
cat(sprintf("M13: Beta+PE+BE/MKTCAP+Dim+Sector  | %9.4f | %9.4f | %9.4f\n",
            summary(m13_15_19)$adj.r.squared, summary(m13_20_24)$adj.r.squared, summary(m13_15_24)$adj.r.squared))
cat(sprintf("M14: Kitchen sink (all variables)  | %9.4f | %9.4f | %9.4f\n",
            summary(m14_15_19)$adj.r.squared, summary(m14_20_24)$adj.r.squared, summary(m14_15_24)$adj.r.squared))


# =============================================================================
# 8. ADDITIONAL INTERESTING COMBINATIONS
# =============================================================================

cat("\n########################################################################\n")
cat("ADDITIONAL MODELS: INTERESTING COMBINATIONS\n")
cat("########################################################################\n\n")

# --- Fama-French inspired: Beta + Size + Value ---
cat("--- Fama-French Style: Return ~ Beta + Dimensions + BE/MKTCAP ---\n\n")

cat("2015-2019:\n")
ff_15_19 <- lm(Return_15_19 ~ Beta + Dimensions + BE_MKTCAP_15_19, data = data_15_19)
print(summary(ff_15_19))

cat("\n2020-2024:\n")
ff_20_24 <- lm(Return_20_24 ~ Beta + Dimensions + BE_MKTCAP_20_24, data = data_20_24)
print(summary(ff_20_24))

cat("\n2015-2024:\n")
ff_15_24 <- lm(Return_15_24 ~ Beta + Dimensions + BE_MKTCAP_15_24, data = data_15_24)
print(summary(ff_15_24))

# --- Sector-specific effects with all factors ---
cat("\n--- Sector Effects with Value Factor ---\n")
cat("Return ~ Sector * BE/MKTCAP (Interaction Model)\n\n")

cat("2015-2019:\n")
int_15_19 <- lm(Return_15_19 ~ Sector * BE_MKTCAP_15_19, data = data_15_19)
print(summary(int_15_19))

cat("\n2020-2024:\n")
int_20_24 <- lm(Return_20_24 ~ Sector * BE_MKTCAP_20_24, data = data_20_24)
print(summary(int_20_24))


# =============================================================================
# 9. CORRELATION MATRICES
# =============================================================================

cat("\n########################################################################\n")
cat("CORRELATION MATRICES\n")
cat("########################################################################\n\n")

cat("=== 2015-2019 Correlations (Return with independent variables) ===\n")
cor_vars_15_19 <- data_15_19[, c("Return_15_19", "Beta", "PE_15_19", 
                                  "TA_MKTCAP_15_19", "TA_BE_15_19", "BE_MKTCAP_15_19")]
print(round(cor(cor_vars_15_19, use = "complete.obs"), 3))

cat("\n=== 2020-2024 Correlations (Return with independent variables) ===\n")
cor_vars_20_24 <- data_20_24[, c("Return_20_24", "Beta", "PE_20_24", 
                                  "TA_MKTCAP_20_24", "TA_BE_20_24", "BE_MKTCAP_20_24")]
print(round(cor(cor_vars_20_24, use = "complete.obs"), 3))

cat("\n=== 2015-2024 Correlations (Return with independent variables) ===\n")
cor_vars_15_24 <- data_15_24[, c("Return_15_24", "Beta", "PE_15_24", 
                                  "TA_MKTCAP_15_24", "TA_BE_15_24", "BE_MKTCAP_15_24")]
print(round(cor(cor_vars_15_24, use = "complete.obs"), 3))


cat("\n========================================================================\n")
cat("ANALYSIS COMPLETE\n")
cat("========================================================================\n")
