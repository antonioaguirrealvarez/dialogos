export interface ConversationAnalysis {
  conversation_summary: string
  communication_depth_distribution: {
    level_1_ritual: string
    level_2_extended_ritual: string
    level_3_surface: string
    level_4_feelings_about_self: string
    level_5_feelings_about_relationship: string
  }
  pentagonal_radar_assessment: {
    self_disclosure: number
    emotional_expression: number
    active_listening: number
    attribution_accuracy: number
    conversation_balance: number
  }
  strengths_and_growth: {
    strengths: string[]
    growth_opportunities: string[]
  }
  key_recommendations: string[]
  detailed_recommendations: Array<{
    title: string
    current_pattern: string
    improvement_opportunity: string
    example_reframing: {
      before: string
      after: string
    }
    benefits: string
    practice_suggestion: string
  }>
  strengths_assessment: Array<{
    strength: string
    effectiveness: string
    leverage: string
  }>
  progress_metrics: string[]
  emotion_analysis?: EmotionAnalysis[]
}

export interface EmotionAnalysis {
  speaker: string
  quintile: number
  main_emotion: string
}
