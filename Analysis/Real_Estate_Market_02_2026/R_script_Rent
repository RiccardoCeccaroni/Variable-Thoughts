# =============================================================================
# REGRESSION ANALYSIS - Italian Rental Market
# Dependent Variable: ln_Prezzo_EUR_mese
# =============================================================================

# --- 1. SETUP & DATA LOADING ------------------------------------------------

library(readxl)
library(corrplot)
library(car)
library(lmtest)
library(sandwich)

df <- read_excel("C:/Users/ricca/Desktop/Real Estate Project/RentForR.xlsx")

# --- 2. DATA CLEANING -------------------------------------------------------

# Remove Tipologia (redundant with Locali)
df$Tipologia <- NULL

# Replace "-" with NA
df[df == "-"] <- NA

# Convert types
df$Locali <- as.numeric(df$Locali)
df$Bagni <- as.numeric(df$Bagni)
df$Ascensore <- as.factor(df$Ascensore)
df$Macro_Regione <- as.factor(df$Macro_Regione)
df$ln_Popolazione_Cap <- as.numeric(df$ln_Popolazione_Cap)
df$ln_Prezzo_EUR_mese <- as.numeric(df$ln_Prezzo_EUR_mese)
df$ln_Metri_Quadri <- as.numeric(df$ln_Metri_Quadri)
df$ln_Distanza_Centro_km <- as.numeric(df$ln_Distanza_Centro_km)

# Set reference levels
df$Macro_Regione <- relevel(df$Macro_Regione, ref = "Nord")
df$Ascensore <- relevel(df$Ascensore, ref = "0")

# Complete cases WITHOUT Ascensore (for Models 1-4)
vars_main <- c("ln_Prezzo_EUR_mese", "ln_Metri_Quadri", "Locali", "Bagni",
               "ln_Distanza_Centro_km", "ln_Popolazione_Cap", "Macro_Regione")
df_main <- df[complete.cases(df[, vars_main]), ]

# Complete cases WITH Ascensore (for Model 5 robustness)
df_full <- na.omit(df)

cat("====== DATA SUMMARY ======\n")
cat("Total observations:", nrow(df), "\n")
cat("Complete cases (Models 1-4):", nrow(df_main), "\n")
cat("Complete cases (Model 5 with Ascensore):", nrow(df_full), "\n\n")
summary(df_main)


# =============================================================================
# 3. CORRELATION MATRIX
# =============================================================================

cat("\n\n====== CORRELATION ANALYSIS ======\n\n")

numeric_vars <- df_main[, c("ln_Prezzo_EUR_mese", "ln_Metri_Quadri", "Locali",
                             "Bagni", "ln_Distanza_Centro_km", "ln_Popolazione_Cap")]

cor_matrix <- cor(numeric_vars, use = "complete.obs")

cat("--- Correlation Matrix ---\n")
print(round(cor_matrix, 3))

# Pairwise tests with p-values
cat("\n--- Pairwise Correlations with P-values ---\n")
vars <- colnames(numeric_vars)
for (i in 1:(length(vars)-1)) {
  for (j in (i+1):length(vars)) {
    test <- cor.test(numeric_vars[[vars[i]]], numeric_vars[[vars[j]]])
    sig <- ifelse(test$p.value < 0.001, "***",
           ifelse(test$p.value < 0.01, "**",
           ifelse(test$p.value < 0.05, "*", "")))
    cat(sprintf("%-25s <-> %-25s  r = %7.4f  p = %.2e  %s\n",
                vars[i], vars[j], test$estimate, test$p.value, sig))
  }
}
cat("\nSignificance: *** p<0.001, ** p<0.01, * p<0.05\n")

# Save correlation plot
png("correlation_matrix.png", width = 900, height = 900, res = 120)
corrplot(cor_matrix, method = "color", type = "upper",
         addCoef.col = "black", number.cex = 0.7,
         tl.col = "black", tl.srt = 45, tl.cex = 0.8,
         title = "Correlation Matrix",
         mar = c(0, 0, 2, 0))
dev.off()


# =============================================================================
# 4. REGRESSION MODELS
# =============================================================================

cat("\n\n========================================================\n")
cat("  REGRESSION MODELS: ln_Prezzo_EUR_mese\n")
cat("========================================================\n\n")

# --- Model 1: Property characteristics only ---
m1 <- lm(ln_Prezzo_EUR_mese ~ ln_Metri_Quadri + Locali + Bagni,
          data = df_main)

# --- Model 2: + Location ---
m2 <- lm(ln_Prezzo_EUR_mese ~ ln_Metri_Quadri + Locali + Bagni +
            ln_Distanza_Centro_km + ln_Popolazione_Cap,
          data = df_main)

# --- Model 3: + Macro Regione ---
m3 <- lm(ln_Prezzo_EUR_mese ~ ln_Metri_Quadri + Locali + Bagni +
            ln_Distanza_Centro_km + ln_Popolazione_Cap + Macro_Regione,
          data = df_main)

# --- Model 4: + Interaction (size x region) ---
m4 <- lm(ln_Prezzo_EUR_mese ~ ln_Metri_Quadri * Macro_Regione +
            Locali + Bagni + ln_Distanza_Centro_km + ln_Popolazione_Cap,
          data = df_main)

# --- Model 5: Robustness - Model 3 + Ascensore (smaller sample) ---
m5 <- lm(ln_Prezzo_EUR_mese ~ ln_Metri_Quadri + Locali + Bagni +
            ln_Distanza_Centro_km + ln_Popolazione_Cap + Macro_Regione +
            Ascensore,
          data = df_full)

# Print all model summaries
cat("--- Model 1: Property Characteristics ---\n")
print(summary(m1))
cat("\n--- Model 2: + Location ---\n")
print(summary(m2))
cat("\n--- Model 3: + Macro Regione ---\n")
print(summary(m3))
cat("\n--- Model 4: + Size x Region Interaction ---\n")
print(summary(m4))
cat("\n--- Model 5: Robustness (+ Ascensore, smaller sample) ---\n")
print(summary(m5))


# =============================================================================
# 5. MODEL COMPARISON
# =============================================================================

cat("\n\n====== MODEL COMPARISON ======\n\n")

cat(sprintf("%-35s  Adj.R²     AIC        BIC        N\n", "Model"))
cat(sprintf("%-35s  %.4f  %10.1f  %10.1f  %6d\n", "M1: Property",
            summary(m1)$adj.r.squared, AIC(m1), BIC(m1), nrow(df_main)))
cat(sprintf("%-35s  %.4f  %10.1f  %10.1f  %6d\n", "M2: + Location",
            summary(m2)$adj.r.squared, AIC(m2), BIC(m2), nrow(df_main)))
cat(sprintf("%-35s  %.4f  %10.1f  %10.1f  %6d\n", "M3: + Macro Regione",
            summary(m3)$adj.r.squared, AIC(m3), BIC(m3), nrow(df_main)))
cat(sprintf("%-35s  %.4f  %10.1f  %10.1f  %6d\n", "M4: + Size x Region",
            summary(m4)$adj.r.squared, AIC(m4), BIC(m4), nrow(df_main)))
cat(sprintf("%-35s  %.4f  %10.1f  %10.1f  %6d\n", "M5: Robustness (+ Ascensore)",
            summary(m5)$adj.r.squared, AIC(m5), BIC(m5), nrow(df_full)))


# =============================================================================
# 6. ANOVA - Nested Model Comparisons (Models 1-4)
# =============================================================================

cat("\n\n====== ANOVA: NESTED MODEL COMPARISONS ======\n\n")

cat("--- M1 vs M2 vs M3 vs M4 ---\n")
print(anova(m1, m2, m3, m4))


# =============================================================================
# 7. VIF - Multicollinearity Check
# =============================================================================

cat("\n\n====== VIF (Model 3 - Main Model) ======\n\n")
print(vif(m3))


# =============================================================================
# 8. HETEROSKEDASTICITY
# =============================================================================

cat("\n\n====== BREUSCH-PAGAN TEST (Model 3) ======\n\n")
print(bptest(m3))

# Robust standard errors for Model 3
cat("\n\n====== ROBUST STANDARD ERRORS (Model 3) ======\n")
cat("(HC1 - corrects for heteroskedasticity)\n\n")
print(coeftest(m3, vcov = vcovHC(m3, type = "HC1")))


# =============================================================================
# 9. STANDARDIZED COEFFICIENTS (Model 3)
# =============================================================================

cat("\n\n====== STANDARDIZED COEFFICIENTS (Model 3) ======\n")
cat("(Comparable effect sizes across variables)\n\n")

df_std <- df_main
num_cols <- c("ln_Prezzo_EUR_mese", "ln_Metri_Quadri", "Locali", "Bagni",
              "ln_Distanza_Centro_km", "ln_Popolazione_Cap")
for (col in num_cols) {
  df_std[[col]] <- scale(df_std[[col]])
}

m3_std <- lm(ln_Prezzo_EUR_mese ~ ln_Metri_Quadri + Locali + Bagni +
               ln_Distanza_Centro_km + ln_Popolazione_Cap + Macro_Regione,
             data = df_std)
print(summary(m3_std))


# =============================================================================
# 10. DIAGNOSTIC PLOTS (Model 3)
# =============================================================================

png("diagnostics_model3.png", width = 1000, height = 800, res = 120)
par(mfrow = c(2, 2))
plot(m3, main = "Diagnostics: Model 3")
dev.off()


cat("\n\n====== ANALYSIS COMPLETE ======\n")
cat("Files saved: correlation_matrix.png, diagnostics_model3.png\n")
