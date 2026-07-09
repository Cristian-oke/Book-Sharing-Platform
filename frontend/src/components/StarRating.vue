<script setup>
import { computed } from 'vue'

//proprietatile componentei pe care le primeste de la parinte
const props = defineProps({
  rating: {
    type: Number,
    required: true,
    default: 0
  },
  maxStars: {
    type: Number,
    default: 5
  }
})

const stars = computed(() => {
  const fullStars = Math.round(props.rating)
  return {
    full: fullStars,
    empty: props.maxStars - fullStars
  }
})
</script>

<template>
  <div class="star-rating" :title="`Rating: ${rating}/5`">
    <span v-for="n in stars.full" :key="'f' + n" class="star full">★</span>
    <span v-for="n in stars.empty" :key="'e' + n" class="star empty">☆</span>
    <span class="rating-text">({{ rating.toFixed(1) }})</span>
  </div>
</template>

<style scoped>
.star-rating {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 1.1rem;
}
.star.full {
  color: #ffca28; 
}
.star.empty {
  color: #ccc;
}
.rating-text {
  font-size: 0.85rem;
  color: #666;
  margin-left: 5px;
}
</style>