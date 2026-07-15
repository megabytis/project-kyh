/* ==========================================================================
   KYH Client Application Logic — Dashboard Integrations & Convo Flow
   ========================================================================== */

const API_BASE = window.location.origin;

// Application State
let userId = "";
let convoStage = "idle";
let activeSession = null;

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const quickReplies = document.getElementById("quick-replies");
const clearConvoBtn = document.getElementById("clear-convo-btn");

const userIdInput = document.getElementById("user-id-input");
const loadUserBtn = document.getElementById("load-user-btn");
const syncStatus = document.getElementById("sync-status");

const triggerSummaryBtn = document.getElementById("trigger-summary-btn");
const showWeeklyReportBtn = document.getElementById("show-weekly-report-btn");

// Macro Elements
const caloriesProgress = document.getElementById("calories-progress");
const caloriesVal = document.getElementById("calories-val");
const proteinVal = document.getElementById("protein-val");
const proteinBar = document.getElementById("protein-bar");
const carbsVal = document.getElementById("carbs-val");
const carbsBar = document.getElementById("carbs-bar");
const fatVal = document.getElementById("fat-val");
const fatBar = document.getElementById("fat-bar");

// Lifestyle Elements
const sleepVal = document.getElementById("sleep-val");
const sleepStatus = document.getElementById("sleep-status");
const waterVal = document.getElementById("water-val");
const waterStatus = document.getElementById("water-status");
const screenVal = document.getElementById("screen-val");
const screenStatus = document.getElementById("screen-status");

// Workout Elements
const workoutVolumeVal = document.getElementById("workout-volume-val");
const cardioDurationVal = document.getElementById("cardio-duration-val");
const workoutDetailsContainer = document.getElementById("workout-details-container");
const mealsDetailsContainer = document.getElementById("meals-details-container");

// AI Coaching Elements
const feedbackText = document.getElementById("feedback-text");
const planText = document.getElementById("plan-text");

// Modal Elements
const weeklyModal = document.getElementById("weekly-modal");
const closeWeeklyBtn = document.getElementById("close-weekly-btn");
const weeklyDaysLogged = document.getElementById("weekly-days-logged");
const weeklyAvgProtein = document.getElementById("weekly-avg-protein");
const weeklyAvgCalories = document.getElementById("weekly-avg-calories");
const weeklyAvgSleep = document.getElementById("weekly-avg-sleep");
const weeklyAvgWater = document.getElementById("weekly-avg-water");
const weeklyAnalysisText = document.getElementById("weekly-analysis-text");
const weeklyPatternsList = document.getElementById("weekly-patterns-list");

// ==========================================================================
// Initialization
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  // Setup event listeners
  chatForm.addEventListener("submit", handleChatSubmit);
  loadUserBtn.addEventListener("load", () => {}); // placeholder
  loadUserBtn.addEventListener("click", () => {
    const rawVal = userIdInput.value.trim();
    if (rawVal) {
      userId = rawVal;
      initSession(userId);
    }
  });

  clearConvoBtn.addEventListener("click", () => {
    // Clear display and reset user
    chatMessages.innerHTML = `
      <div class="message system">
        <div class="message-content">
          <p>Conversation log reset. Reinitializing today's session...</p>
        </div>
      </div>
    `;
    initSession(userId);
  });

  triggerSummaryBtn.addEventListener("click", () => {
    sendMessageToServer("daily summary");
  });

  showWeeklyReportBtn.addEventListener("click", openWeeklyReport);
  closeWeeklyBtn.addEventListener("click", () => weeklyModal.classList.remove("active"));
  
  // Close modal when clicking outside
  window.addEventListener("click", (e) => {
    if (e.target === weeklyModal) {
      weeklyModal.classList.remove("active");
    }
  });

  // Initial load — only if a userId is already stored
  if (userId) initSession(userId);
});

// ==========================================================================
// Session Syncing
// ==========================================================================

async function initSession(user) {
  setSyncing(true);
  try {
    const response = await fetch(`${API_BASE}/api/session?userId=${encodeURIComponent(user)}`);
    if (!response.ok) throw new Error("Failed to initialize session");
    
    const data = await response.json();
    activeSession = data.session;
    convoStage = data.stage || "idle";
    
    setSyncing(false, "Connected");
    
    // Update Dashboard representation
    updateDashboard(activeSession);
    
    // Render quick suggestion buttons
    renderQuickReplies(convoStage);
    
    // Render past messages from session if they exist
    renderHistory(activeSession.messages);
    
  } catch (error) {
    console.error("Init session error:", error);
    setSyncing(false, "Offline", true);
    addSystemMessage("⚠️ Could not reach backend. Check that Node.js server is running on port 3000.");
  }
}

function setSyncing(isSyncing, message = "Connected", isError = false) {
  if (isSyncing) {
    syncStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Syncing...`;
    syncStatus.style.color = "var(--text-secondary)";
  } else {
    if (isError) {
      syncStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${message}`;
      syncStatus.style.color = "var(--color-calories)";
    } else {
      syncStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${message}`;
      syncStatus.style.color = "#10b981";
    }
  }
}

// ==========================================================================
// Chat Interaction
// ==========================================================================

async function handleChatSubmit(e) {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;
  
  chatInput.value = "";
  sendMessageToServer(text);
}

async function sendMessageToServer(messageText) {
  // Append user message
  appendMessage("user", messageText);
  
  // Show typing indicator
  const typingElem = showTypingIndicator();
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId: userId, message: messageText })
    });
    
    // Remove typing indicator
    typingElem.remove();
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.reply || "Failed to process chat");
    }

    const data = await response.json();
    convoStage = data.stage || "idle";
    activeSession = data.session || activeSession;
    
    // Append Bot reply
    appendMessage("bot", data.reply);
    
    // Update dashboard visual values
    updateDashboard(activeSession);
    
    // Render new set of quick replies
    renderQuickReplies(convoStage);
    
  } catch (error) {
    typingElem.remove();
    console.error("Chat message error:", error);
    appendMessage("bot", `⚠️ Error: ${error.message || "Failed to contact agent."}`);
  }
  
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Render Messages UI helpers

// Strip raw JSON blocks from bot reply text before displaying in chat
function stripJsonFromReply(text) {
  if (!text) return "";

  // Remove fenced code blocks (```json ... ``` or ``` ... ```)
  text = text.replace(/```[\s\S]*?```/gi, "");

  // Remove any {...} block structurally using brace counting
  // This catches both valid and malformed/partial JSON
  let result = "";
  let depth = 0;
  let inBlock = false;
  let i = 0;

  while (i < text.length) {
    const ch = text[i];
    if (ch === "{") {
      depth++;
      inBlock = true;
    } else if (ch === "}") {
      depth = Math.max(0, depth - 1);
      if (depth === 0 && inBlock) {
        inBlock = false;
        i++; // skip closing brace
        // also skip the newline right after if present
        if (text[i] === "\n") i++;
        continue;
      }
    } else if (!inBlock) {
      result += ch;
    }
    i++;
  }

  // Also remove bare JSON arrays [ ... ] that span multiple lines
  result = result.replace(/\[[\s\S]*?\]/g, (match) => {
    // Only strip if it contains object-like content
    if (match.includes('"') && (match.includes("name") || match.includes("exercise") || match.includes("sets"))) {
      return "";
    }
    return match;
  });

  // Collapse multiple blank lines
  result = result.replace(/\n{3,}/g, "\n\n").trim();
  return result;
}

function appendMessage(sender, text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}`;
  
  // Strip any raw JSON blobs from bot messages
  let cleanText = sender === "bot" ? stripJsonFromReply(text) : (text || "");
  cleanText = cleanText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  cleanText = cleanText.replace(/\*(.*?)\*/g, "<em>$1</em>");
  
  msgDiv.innerHTML = `
    <div class="message-content">
      <p>${cleanText}</p>
    </div>
  `;
  chatMessages.appendChild(msgDiv);
}

function addSystemMessage(text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = "message system";
  msgDiv.innerHTML = `
    <div class="message-content">
      <p>${text}</p>
    </div>
  `;
  chatMessages.appendChild(msgDiv);
}

function showTypingIndicator() {
  const typingDiv = document.createElement("div");
  typingDiv.className = "message bot typing-indicator-container";
  typingDiv.innerHTML = `
    <div class="message-content typing-indicator">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  chatMessages.appendChild(typingDiv);
  return typingDiv;
}

// Render historical chat messages from db session
function renderHistory(messages) {
  // Don't replay chat history on sync — the dashboard already shows all logged data.
  // Just confirm how many logs are on record so the user knows their session loaded.
  if (!messages || messages.length === 0) return;

  const userMsgs = messages.filter(m => m.type === "human" || m.id?.includes("HumanMessage"));
  if (userMsgs.length > 0) {
    addSystemMessage(`📂 Session restored — ${userMsgs.length} message${userMsgs.length > 1 ? "s" : ""} on record. Your logged data is reflected in the dashboard →`);
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ==========================================================================
// Quick Reply Chips Generator
// ==========================================================================

function renderQuickReplies(stage) {
  quickReplies.innerHTML = "";
  
  let chips = [];
  
  switch(stage) {
    case "awaiting_category":
      chips = [
        { text: "food", label: "🍽️ Log Food" },
        { text: "workout", label: "🏋️ Log Workout" },
        { text: "others", label: "😴 Log Sleep / Water" },
        { text: "daily summary", label: "📊 Daily Summary" }
      ];
      break;
    case "awaiting_meal_type":
      chips = [
        { text: "breakfast", label: "🌅 Breakfast" },
        { text: "lunch", label: "☀️ Lunch" },
        { text: "dinner", label: "🌙 Dinner" },
        { text: "snacks", label: "🍪 Snacks" }
      ];
      break;
    case "awaiting_workout_type":
      chips = [
        { text: "weight training", label: "🏋️ Weight Training" },
        { text: "cardio", label: "🏃 Cardio" }
      ];
      break;
    case "awaiting_others_category":
      chips = [
        { text: "sleep", label: "😴 Sleep Duration" },
        { text: "water", label: "💧 Water Intake" },
        { text: "screen time", label: "📱 Screen Time" }
      ];
      break;
    case "idle":
      chips = [
        { text: "food", label: "🍽️ Add Food" },
        { text: "workout", label: "🏋️ Add Workout" },
        { text: "others", label: "😴 Add Others" },
        { text: "daily summary", label: "📊 Daily Summary" }
      ];
      break;
    default:
      chips = [
        { text: "food", label: "🍽️ Food" },
        { text: "workout", label: "🏋️ Workout" },
        { text: "others", label: "Others" }
      ];
  }
  
  chips.forEach(chip => {
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.innerHTML = chip.label;
    btn.addEventListener("click", () => {
      sendMessageToServer(chip.text);
    });
    quickReplies.appendChild(btn);
  });
}

// ==========================================================================
// Dashboard Value Syncing
// ==========================================================================

function updateDashboard(session) {
  if (!session) return;
  
  // Calculate Totals Client-side (in case Daily Summary hasn't run yet)
  let protein = 0;
  let carbs = 0;
  let fat = 0;
  let calories = 0;
  
  if (session.meals) {
    Object.values(session.meals).forEach(meal => {
      if (meal.macros) {
        protein += Number(meal.macros.protein) || 0;
        carbs += Number(meal.macros.carbs) || 0;
        fat += Number(meal.macros.fat) || 0;
        calories += Number(meal.macros.calories) || 0;
      }
    });
  }

  // Override with dailyTotals if summary is generated
  if (session.summaryGenerated && session.dailyTotals) {
    protein = session.dailyTotals.protein || protein;
    carbs = session.dailyTotals.carbs || carbs;
    fat = session.dailyTotals.fat || fat;
    calories = session.dailyTotals.calories || calories;
  }
  
  // Update Macros GUI
  caloriesVal.textContent = Math.round(calories);
  proteinVal.textContent = Math.round(protein);
  carbsVal.textContent = Math.round(carbs);
  fatVal.textContent = Math.round(fat);
  
  // Set Circular Progress Percentage (Calories target = 2000)
  const caloriesPercent = Math.min(100, Math.round((calories / 2000) * 100));
  caloriesProgress.style.setProperty("--percent", caloriesPercent);
  
  // Set linear macro bar fill widths
  proteinBar.style.width = `${Math.min(100, Math.round((protein / 110) * 100))}%`;
  carbsBar.style.width = `${Math.min(100, Math.round((carbs / 200) * 100))}%`;
  fatBar.style.width = `${Math.min(100, Math.round((fat / 60) * 100))}%`;

  // Update Lifestyle Metrics
  let sleepHours = 0;
  let waterLiters = 0;
  let screenMinutes = 0;
  
  if (session.others) {
    if (session.others.sleep) {
      sleepHours = Number(session.others.sleep.total_hours) || Number(session.others.sleep.value) || 0;
      // If total_hours is missing but from/to is present
      if (!sleepHours && session.others.sleep.from && session.others.sleep.to) {
        sleepHours = calculateTimeDiff(session.others.sleep.from, session.others.sleep.to);
      }
    }
    if (session.others.water) {
      // water can be just count (glasses) or liters
      const waterValRaw = Number(session.others.water.value) || Number(session.others.water) || 0;
      const unit = session.others.water.unit || "glasses";
      if (unit === "glasses") {
        waterLiters = waterValRaw * 0.25; // 250ml per glass
      } else {
        waterLiters = waterValRaw;
      }
    }
    if (session.others.screen_time) {
      screenMinutes = Number(session.others.screen_time.value) || Number(session.others.screen_time) || 0;
    }
  }

  // Override with dailyTotals if summary is generated
  if (session.summaryGenerated && session.dailyTotals) {
    sleepHours = session.dailyTotals.sleep_hours || sleepHours;
    // Water in daily totals might be numeric
    if (session.dailyTotals.water) {
      waterLiters = session.dailyTotals.water;
    }
  }

  sleepVal.textContent = sleepHours.toFixed(1);
  waterVal.textContent = waterLiters.toFixed(1);
  screenVal.textContent = screenMinutes;
  
  // Status check styling
  sleepStatus.textContent = sleepHours >= 7 ? "Target reached! ✅" : "Deficit: Log sleep";
  sleepStatus.style.color = sleepHours >= 7 ? "#10b981" : "var(--text-muted)";
  
  waterStatus.textContent = waterLiters >= 4.0 ? "Target reached! ✅" : `${(4.0 - waterLiters).toFixed(1)}L short`;
  waterStatus.style.color = waterLiters >= 4.0 ? "#10b981" : "var(--text-muted)";
  
  screenStatus.textContent = screenMinutes <= 180 ? "Good limit ✅" : `${screenMinutes - 180} min over`;
  screenStatus.style.color = screenMinutes <= 180 ? "#10b981" : "var(--color-screen)";

  // Update Workouts volume
  let workoutVol = 0;
  let cardioDur = 0;
  
  if (session.workout) {
    if (session.workout.weight_training) {
      session.workout.weight_training.forEach(ex => {
        if (ex.sets) {
          ex.sets.forEach(s => {
            const w = Number(s.weight) || 0;
            const r = Number(s.reps) || 0;
            workoutVol += w * r;
          });
        }
      });
    }
    if (session.workout.cardio) {
      session.workout.cardio.forEach(c => {
        cardioDur += Number(c.duration) || 0;
      });
    }
  }

  workoutVolumeVal.textContent = Math.round(workoutVol);
  cardioDurationVal.textContent = cardioDur;

  // Render Exercises Details list
  renderWorkoutDetails(session.workout);

  // Render Meals Details list
  renderMealsDetails(session.meals);

  // Update AI feedback
  if (session.feedback) {
    feedbackText.textContent = session.feedback;
  } else {
    feedbackText.innerHTML = `Complete logging your day and click <strong>Daily Summary</strong> to get personalized coaching feedback from your LangGraph AI.`;
  }
  
  if (session.plan) {
    planText.textContent = session.plan;
  } else {
    planText.textContent = "Your target plan will appear here after the daily summary completes.";
  }
}

// Render workout details inside dashboard
function renderWorkoutDetails(workout) {
  if (!workout || (!workout.weight_training && !workout.cardio)) {
    workoutDetailsContainer.className = "details-placeholder";
    workoutDetailsContainer.textContent = "No workout exercises logged today yet.";
    return;
  }

  workoutDetailsContainer.className = ""; // clear placeholder
  workoutDetailsContainer.innerHTML = "";

  // Render weights
  if (workout.weight_training && workout.weight_training.length > 0) {
    workout.weight_training.forEach(ex => {
      const item = document.createElement("div");
      item.className = "exercise-detail-item";
      
      let exVol = 0;
      let setsHTML = "";
      
      if (ex.sets) {
        ex.sets.forEach((s, idx) => {
          exVol += (Number(s.weight) || 0) * (Number(s.reps) || 0);
          setsHTML += `<span class="set-pill">S${idx+1}: ${s.weight}kg x ${s.reps}</span>`;
        });
      }
      
      item.innerHTML = `
        <div class="exercise-title">
          <span class="name"><i class="fa-solid fa-dumbbell"></i> ${ex.exercise_name}</span>
          <span class="volume-tag">${exVol} kg vol</span>
        </div>
        <div class="sets-pills">${setsHTML}</div>
      `;
      workoutDetailsContainer.appendChild(item);
    });
  }

  // Render cardio
  if (workout.cardio && workout.cardio.length > 0) {
    workout.cardio.forEach(c => {
      const item = document.createElement("div");
      item.className = "exercise-detail-item";
      item.innerHTML = `
        <div class="exercise-title">
          <span class="name"><i class="fa-solid fa-person-running"></i> ${c.name}</span>
          <span class="volume-tag">${c.duration} min</span>
        </div>
      `;
      workoutDetailsContainer.appendChild(item);
    });
  }
}

// Render meals details cards in dashboard list
function renderMealsDetails(meals) {
  if (!meals || Object.keys(meals).length === 0) {
    mealsDetailsContainer.innerHTML = `<div class="details-placeholder">No food meals logged today yet.</div>`;
    return;
  }

  mealsDetailsContainer.innerHTML = "";
  
  Object.keys(meals).forEach(mealKey => {
    const meal = meals[mealKey];
    const card = document.createElement("div");
    card.className = "meal-detail-card";
    
    let itemsHTML = "";
    if (meal.foods) {
      meal.foods.forEach(f => {
        itemsHTML += `<li>${f.name} - ${f.quantity} ${f.unit || "pieces"}</li>`;
      });
    }

    const p = Math.round(meal.macros?.protein || 0);
    const c = Math.round(meal.macros?.carbs || 0);
    const f = Math.round(meal.macros?.fat || 0);
    const cal = Math.round(meal.macros?.calories || 0);

    card.innerHTML = `
      <div class="meal-detail-card-header ${mealKey}">
        <h3>${mealKey}</h3>
        <div class="meal-macro-badges">
          <span class="macro-badge" style="border-left: 2px solid var(--color-protein)">P: <strong>${p}g</strong></span>
          <span class="macro-badge" style="border-left: 2px solid var(--color-carbs)">C: <strong>${c}g</strong></span>
          <span class="macro-badge" style="border-left: 2px solid var(--color-fat)">F: <strong>${f}g</strong></span>
          <span class="macro-badge" style="border-left: 2px solid var(--color-calories)"><strong>${cal} cal</strong></span>
        </div>
      </div>
      <ul class="meal-items-list">
        ${itemsHTML || "<li>No details registered</li>"}
      </ul>
    `;
    mealsDetailsContainer.appendChild(card);
  });
}

// Helper to calculate hour difference
function calculateTimeDiff(from, to) {
  try {
    const [fHr, fMin] = from.split(":").map(Number);
    const [tHr, tMin] = to.split(":").map(Number);
    
    let diffMins = (tHr * 60 + tMin) - (fHr * 60 + fMin);
    if (diffMins < 0) {
      diffMins += 24 * 60; // Slept over midnight
    }
    return diffMins / 60;
  } catch (e) {
    return 0;
  }
}

// ==========================================================================
// Weekly Report Modal Loader
// ==========================================================================

async function openWeeklyReport() {
  weeklyModal.classList.add("active");
  weeklyAnalysisText.textContent = "Fetching weekly analytics and generating report from AI engine...";
  weeklyPatternsList.innerHTML = "";
  
  weeklyDaysLogged.textContent = "-";
  weeklyAvgProtein.textContent = "-";
  weeklyAvgCalories.textContent = "-";
  weeklyAvgSleep.textContent = "-";
  weeklyAvgWater.textContent = "-";

  try {
    const response = await fetch(`${API_BASE}/api/report?userId=${encodeURIComponent(userId)}`);
    if (!response.ok) throw new Error("Could not fetch weekly report");
    
    const data = await response.json();
    
    // Fill numbers
    const summary = data.weekly_summary || {};
    weeklyDaysLogged.textContent = `${summary.total_days || 0} / 7`;
    weeklyAvgProtein.textContent = Math.round(summary.avg_protein || 0);
    weeklyAvgCalories.textContent = Math.round(summary.avg_calories || 0);
    weeklyAvgSleep.textContent = (summary.avg_sleep || 0).toFixed(1);
    weeklyAvgWater.textContent = (summary.avg_water || 0).toFixed(1);

    // AI Analysis Report text
    let cleanReport = data.weekly_report || "No analysis available.";
    cleanReport = cleanReport.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    cleanReport = cleanReport.replace(/\*(.*?)\*/g, "<em>$1</em>");
    weeklyAnalysisText.innerHTML = cleanReport;

    // Consistency checklist
    let listHTML = "";
    
    // Protein missing tracker
    if (summary.days_below_protein && summary.days_below_protein.length > 0) {
      listHTML += `<li><i class="fa-solid fa-triangle-exclamation alert"></i> Protein fell short (<90g) on days: <strong>${summary.days_below_protein.join(", ")}</strong></li>`;
    } else {
      listHTML += `<li><i class="fa-solid fa-circle-check check"></i> Hit protein threshold consistently!</li>`;
    }
    
    // Workouts skipped tracker
    if (summary.days_missing_workout && summary.days_missing_workout.length > 0) {
      listHTML += `<li><i class="fa-solid fa-xmark cross"></i> Missed workouts on days: <strong>${summary.days_missing_workout.join(", ")}</strong></li>`;
    } else {
      listHTML += `<li><i class="fa-solid fa-circle-check check"></i> Workouts fully registered!</li>`;
    }

    // Water skipped tracker
    if (summary.days_missing_water && summary.days_missing_water.length > 0) {
      listHTML += `<li><i class="fa-solid fa-droplet-slash cross"></i> Dehydration (no water logged) on days: <strong>${summary.days_missing_water.join(", ")}</strong></li>`;
    } else {
      listHTML += `<li><i class="fa-solid fa-circle-check check"></i> Hydration records complete!</li>`;
    }
    
    weeklyPatternsList.innerHTML = listHTML || '<li><i class="fa-solid fa-circle-check check"></i> Perfect consistency recorded this week!</li>';

  } catch(e) {
    console.error(e);
    weeklyAnalysisText.innerHTML = `<span style="color: var(--color-calories)">⚠️ Error loading report: ${e.message || "Is Python agent server active?"}</span>`;
  }
}
