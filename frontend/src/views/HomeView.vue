<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import StarRating from '../components/StarRating.vue'

const router = useRouter()
const searchQuery = ref('')
const books = ref([]) // Va fi populat din Backend
const isLoading = ref(true)
const errorMessage = ref('')

const API_URL = 'http://localhost:5000/Book_Sharing/books/view-books' 

// aduce datele din flask
const fetchBooks = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(API_URL)
    books.value = response.data
  } catch (error) {
    console.error("Eroare la conectarea cu Flask:", error)
    errorMessage.value = "Nu s-a putut face conexiunea cu serverul. Folosim date de test."
    
    //date de test
    books.value = [
      { id: 1, title: 'Amintiri din copilărie', author: 'Ion Creangă', city: 'București', condition: 'Bună', image_url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400', rating: 4.5, available: true },
      { id: 2, title: 'Cel mai iubit dintre pământeni', author: 'Marin Preda', city: 'Iași', condition: 'Uzată', image_url: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400', rating: 4.8, available: false },
      { id: 3, title: 'Atomic Habits', author: 'James Clear', city: 'București', condition: 'Nouă', image_url: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400', rating: 4.9, available: true }
    ]
  } finally {
    isLoading.value = false
  }
}

// Rulăm funcția automat când se încarcă componenta în browser
onMounted(() => {
  fetchBooks()
})

const filteredBooks = computed(() => {
  if (!searchQuery.value) return books.value
  
  const query = searchQuery.value.toLowerCase().trim()
  return books.value.filter(book => 
    book.title.toLowerCase().includes(query) || 
    book.author.toLowerCase().includes(query) ||
    book.city.toLowerCase().includes(query)
  )
})

const viewDetails = (bookId) => {
  router.push({ name: 'book-details', params: { id: bookId } })
}
</script>

<template>
  <div class="catalog-container">
    <header class="catalog-header">
      <h2>Catalogul de Cărți</h2>
      <p>Descoperă cărți adăugate de comunitate și cere-le la împrumut!</p>
      
      <div class="search-bar-container">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Caută după titlu, autor sau orașul proprietarului..." 
          class="search-input"
        />
        <span v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">✕</span>
      </div>
    </header>

    <div v-if="isLoading" class="loading-state">
      <p>Se încarcă catalogul...</p>
    </div>

    <div v-if="errorMessage" class="api-warning">
      ⚠️ {{ errorMessage }}
    </div>

    <div v-if="!isLoading && filteredBooks.length === 0" class="no-results">
      <p>Nu am găsit nicio carte care să corespundă căutării tale. 🔍</p>
    </div>

    <div v-if="!isLoading && filteredBooks.length > 0" class="books-grid">
      <div 
        v-for="book in filteredBooks" 
        :key="book.id" 
        class="book-card"
        @click="viewDetails(book.id)"
      >
        <div class="image-wrapper">
          <img 
            :src="book.image_url || 'https://via.placeholder.com/400x500?text=Fara+Imagine'" 
            :alt="book.title" 
            class="book-image"
          />
          <div class="book-status" :class="{ 'available': book.available, 'borrowed': !book.available }">
            {{ book.available ? 'Disponibilă' : 'Împrumutată' }}
          </div>
        </div>
        
        <div class="card-body">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author">de {{ book.author }}</p>
          
          <div class="meta-tags">
            <span class="book-city">📍 {{ book.city }}</span>
            <span class="book-condition" :class="book.condition?.toLowerCase()">✨ Stare: {{ book.condition || 'Nespecificată' }}</span>
          </div>
        </div>
        
        <div class="card-footer">
          <div class="owner-rating">
            <small>Proprietar:</small>
            <StarRating :rating="book.rating" />
          </div>
          <button class="details-btn">Vezi detalii</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.catalog-header {
  text-align: center;
  margin-bottom: 40px;
}

.search-bar-container {
  position: relative;
  max-width: 500px;
  margin: 20px auto 0 auto;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 15px;
  font-size: 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #42b983;
}

.clear-btn {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
}

.loading-state, .api-warning {
  text-align: center;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 8px;
}
.api-warning {
  background-color: #fff3cd;
  color: #856404;
  font-size: 0.9rem;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 30px;
}

.book-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
  border: 1px solid #eef0f2;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.22s, box-shadow 0.22s;
}

.book-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.12);
}

/* Stiluri pentru Imagine */
.image-wrapper {
  position: relative;
  width: 100%;
  height: 280px;
  background-color: #f5f5f5;
}

.book-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-status {
  position: absolute;
  top: 12px;
  left: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.book-status.available {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.book-status.borrowed {
  background-color: #ffebee;
  color: #c62828;
}

.card-body {
  padding: 15px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.book-title {
  margin: 0 0 5px 0;
  font-size: 1.15rem;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-author {
  margin: 0 0 12px 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

.book-city, .book-condition {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.book-city {
  background: #eef2f7;
  color: #34495e;
}

/* Culori dinamice bazate pe starea cărții */
.book-condition {
  background: #f1f3f5;
  color: #495057;
}
.book-condition.nouă { background: #e3f2fd; color: #0d47a1; }
.book-condition.bună { background: #e8f5e9; color: #1b5e20; }
.book-condition.uzată { background: #fff3e0; color: #e65100; }

.card-footer {
  padding: 12px 15px;
  background: #fafbfc;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.owner-rating {
  display: flex;
  flex-direction: column;
}
.owner-rating small {
  font-size: 0.7rem;
  color: #95a5a6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.details-btn {
  background: transparent;
  border: 1px solid #42b983;
  color: #42b983;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
}

.book-card:hover .details-btn {
  background: #42b983;
  color: white;
}

.no-results {
  text-align: center;
  margin-top: 30px;
  color: #780606;
  font-weight: bold;
}
</style>