# Investor Event Assistant Android App - Development Plan

## App Overview

An Android application to assist during investor events by providing comprehensive information about investment companies through fuzzy search, detailed company profiles, and real-time news integration using Gemini AI.

## Architecture Overview

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM with Repository pattern
- **Data Sources**: Local CSV + Gemini API
- **Key Libraries**:
  - Google Generative AI SDK
  - CSV parser
  - Compose Navigation
  - Retrofit (for potential web requests)
  - Coil (for image loading)

## Phase 1: Project Setup & Basic Structure

### Tasks:

1. **Update build.gradle.kts dependencies**

   - Add Jetpack Compose BOM
   - Add Google Generative AI SDK
   - Add CSV parsing library (OpenCSV)
   - Add Navigation Compose
   - Add ViewModel & LiveData
   - Add Coroutines
   - Add Material3

2. **Create project structure**

   - Create packages: `data`, `domain`, `presentation`, `utils`
   - Set up MVVM architecture folders

3. **Setup Gemini API integration**
   - Add API key configuration
   - Create Gemini service class
   - Test basic API connectivity

## Phase 2: Data Layer Implementation

### Tasks:

1. **CSV Data Model**

   - Create `Investor` data class with all CSV fields
   - Implement CSV parser to read Yogen.csv from assets
   - Create InvestorRepository

2. **Fuzzy Search Implementation**

   - Implement fuzzy string matching algorithm
   - Create search functionality that handles partial matches
   - Test search with examples like "Brydon" → "The Brydon Group"

3. **Gemini API Integration**
   - Create prompts for company information
   - Create prompts for news articles
   - Implement API calls with proper error handling
   - Create data models for Gemini responses

## Phase 3: UI Implementation - Search Screen

### Tasks:

1. **Search Screen Design**

   - Create search text field with dropdown
   - Implement real-time search suggestions
   - Add "Investor Details" button
   - Style with Material3 design

2. **Search Functionality**
   - Connect search UI to fuzzy search logic
   - Implement dropdown with search results
   - Add search result selection handling

## Phase 4: UI Implementation - Details Screen

### Tasks:

1. **Details Screen Layout**

   - Create tabbed interface (Company Information, News)
   - Design company information card layout
   - Implement scrollable content

2. **Company Information Tab**

   - Display basic info from CSV (AUM, PE Category, etc.)
   - Show Gemini-generated content (About, What they do, Major Investments)
   - Organize information in logical, aesthetic order

3. **News Tab**
   - Display news articles from Gemini
   - Implement link previews if possible
   - Add loading states and error handling

## Phase 5: Gemini API Prompts & Integration

### Tasks:

1. **Company Information Prompts**

   - "About the Company" prompt
   - "What they do" prompt
   - "Major Investments" prompt

2. **News Articles Prompt**

   - Implement the provided news template
   - Parse structured response from Gemini
   - Handle verification and link validation

3. **API Error Handling**
   - Add retry mechanisms
   - Implement fallback for offline mode
   - Add loading indicators

## Phase 6: Polish & Enhancement

### Tasks:

1. **UI/UX Improvements**

   - Add animations and transitions
   - Implement proper loading states
   - Add error messages and empty states
   - Optimize for different screen sizes

2. **Performance Optimization**

   - Implement caching for Gemini responses
   - Optimize CSV parsing
   - Add pagination for large datasets

3. **Link Preview Implementation**
   - Research and implement link preview functionality
   - Add metadata extraction for news links
   - Handle different URL formats

## Phase 7: Testing & Final Polish

### Tasks:

1. **Testing**

   - Unit tests for search functionality
   - Integration tests for Gemini API
   - UI tests for navigation flows

2. **Final Polish**
   - Add app icon and branding
   - Implement proper error handling
   - Add accessibility features
   - Performance testing

## Technical Requirements

### Dependencies to Add:

```kotlin
// Jetpack Compose
implementation platform('androidx.compose:compose-bom:2024.02.00')
implementation 'androidx.compose.ui:ui'
implementation 'androidx.compose.material3:material3'
implementation 'androidx.activity:activity-compose'
implementation 'androidx.navigation:navigation-compose'

// ViewModel
implementation 'androidx.lifecycle:lifecycle-viewmodel-compose'

// Gemini AI
implementation 'com.google.ai.client.generativeai:generativeai:0.2.2'

// CSV parsing
implementation 'com.opencsv:opencsv:5.7.1'

// Coroutines
implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android'

// Image loading
implementation 'io.coil-kt:coil-compose:2.4.0'
```

### File Structure:

```
app/src/main/java/com/yogen/eventassistant/
├── data/
│   ├── model/
│   │   ├── Investor.kt
│   │   ├── GeminiResponse.kt
│   │   └── NewsArticle.kt
│   ├── repository/
│   │   ├── InvestorRepository.kt
│   │   └── GeminiRepository.kt
│   └── source/
│       ├── CsvDataSource.kt
│       └── GeminiApiService.kt
├── domain/
│   ├── usecase/
│   │   ├── SearchInvestorsUseCase.kt
│   │   ├── GetInvestorDetailsUseCase.kt
│   │   └── GetNewsArticlesUseCase.kt
│   └── util/
│       └── FuzzySearchUtil.kt
├── presentation/
│   ├── search/
│   │   ├── SearchScreen.kt
│   │   ├── SearchViewModel.kt
│   │   └── SearchState.kt
│   ├── details/
│   │   ├── DetailsScreen.kt
│   │   ├── DetailsViewModel.kt
│   │   ├── DetailsState.kt
│   │   ├── CompanyInfoTab.kt
│   │   └── NewsTab.kt
│   ├── navigation/
│   │   └── Navigation.kt
│   └── theme/
│       ├── Color.kt
│       ├── Theme.kt
│       └── Type.kt
└── utils/
    ├── Constants.kt
    └── Extensions.kt
```

## Data Display Order (Details Screen):

1. **Header Section**

   - Investor Name
   - Primary Investor Type
   - HQ Location & Country

2. **Key Metrics**

   - AUM (Assets Under Management)
   - PE Category
   - Investments | Active Portfolio | Exits
   - Investments in last 12 months
   - Dry Powder

3. **AI-Generated Content**
   - About the Company
   - What they do
   - Major Investments

## Estimated Timeline:

- **Phase 1-2**: 2-3 days
- **Phase 3-4**: 3-4 days
- **Phase 5**: 2-3 days
- **Phase 6-7**: 2-3 days
- **Total**: 9-13 days

## API Key Setup:

- Store Gemini API key in `local.properties`
- Access via BuildConfig in the app
- Implement proper key management for production

This plan provides a structured approach to building your investor event assistant app with all the requested features including fuzzy search, Gemini AI integration, and news article display.
