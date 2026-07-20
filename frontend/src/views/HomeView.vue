<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import StarRating from '../components/StarRating.vue'
import { isAuthenticated, token } from '../auth' 

const router = useRouter()
const searchQuery = ref('')
const books = ref([]) 
const isLoading = ref(true)
const errorMessage = ref('')

const API_URL = 'http://localhost:5000/Book_Sharing/books/view-books' 
const BASE_URL = 'http://localhost:5000'

//aflarea userului curent logat
const currentUserId = computed(() => {
  if (!token.value) return null
  
  try {
    const base64Url = token.value.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    const decoded = JSON.parse(jsonPayload)
    
    return decoded.sub ? parseInt(decoded.sub) : null
  } catch (error) {
    console.error("Eroare la decodificarea token-ului:", error)
    return null
  }
})

const fetchBooks = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(API_URL)
    books.value = response.data
  } catch (error) {
    console.error("Eroare la conectarea cu Flask:", error)
    errorMessage.value = "Nu s-a putut face conexiunea cu serverul-Folosire date de test"
    
    //date de test
    books.value = [
      { id: 1, title: 'Amintiri din copilărie', author: 'Ion Creangă', city: 'București', status: 'Bună', image_url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400', owner_rating: 4.5, availability: 'Disponibila', user_id: 10 },
      { id: 2, title: 'Cel mai iubit dintre pământeni', author: 'Marin Preda', city: 'Iași', status: 'Uzată', image_url: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400', owner_rating: 4.8, availability: 'Imprumutata', user_id: 11 },
      { id: 3, title: 'Atomic Habits', author: 'James Clear', city: 'București', status: 'Nouă', image_url: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400', owner_rating: 4.9, availability: 'Disponibila', user_id: 12 }
    ]
  } finally {
    isLoading.value = false
  }
}

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

const viewOwnerProfile = (ownerId) => {
  if (!ownerId) return
  router.push(`/user/${ownerId}`)
}

const handleRequestBook = async (bookId, bookTitle) => {
  if (!isAuthenticated.value) {
    alert("Trebuie să fii logat pentru a cere o carte!")
    router.push('/login')
    return
  }
  
  if (confirm(`Vrei să trimiți o cerere de împrumut pentru "${bookTitle}"?`)) {
    try {
      const config = { headers: { Authorization: `Bearer ${token.value}` } }
      const response = await axios.post(`${BASE_URL}/Book_Sharing/loans/request/${bookId}`, {}, config)
      alert(response.data.message || "Cererea a fost trimisă cu succes proprietarului!")
      await fetchBooks()
    } catch (err) {
      alert(err.response?.data?.error || "Eroare la trimiterea cererii.")
    }
  }
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
          class="search-input"/>
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
      >
        <div class="image-wrapper">
          <img 
            :src="book.image_url || '/default-image.jpg'" 
            :alt="book.title" 
            class="book-image"
          />
          <div class="book-status" :class="{ 'available': book.availability === 'Disponibila', 'Imprumutata': book.availability !== 'Disponibila' }">
            {{ book.availability === 'Disponibila' ? 'Disponibilă' : 'Indisponibilă' }}
          </div>
        </div>
        
        <div class="card-body">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author">de {{ book.author }}</p>
          
          <div class="meta-tags">
            <span class="book-city">📍 {{ book.city }}</span>
            <span class="book-condition" :class="book.status?.toLowerCase()">✨ Stare: {{ book.status }}</span>
          </div>
        </div>
        
        <div class="card-footer-buttons">
          <div v-if="currentUserId === book.user_id" class="own-book-message">
            ℹ️ Această carte îți aparține
          </div>

          <template v-else>
            <div class="owner-rating-box">
              <small>Rating proprietar:</small>
              <StarRating :rating="book.owner_rating || 0" />
            </div>
            
            <div class="actions-wrapper">
              <button class="profile-btn" @click="viewOwnerProfile(book.user_id)">👤 Profil Proprietar</button>
              <button 
                v-if="book.availability === 'Disponibila'" 
                class="request-btn" 
                @click="handleRequestBook(book.id, book.title)"
              >
                ➕ Cere Cartea
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.catalog-header { text-align: center; margin-bottom: 40px; }
.search-bar-container { position: relative; max-width: 500px; margin: 20px auto 0 auto; }
.search-input { width: 100%; padding: 12px 40px 12px 15px; font-size: 1rem; border: 2px solid #dee2e6; border-radius: 8px; outline: none; transition: border-color 0.2s; }
.search-input:focus { border-color: #42b983; }
.clear-btn { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; color: #999; }

.loading-state {text-align: center; padding: 40px; font-weight: bold; color: #7f8c8d;}
.api-warning { text-align: center; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
.api-warning { background-color: #fff3cd; color: #856404; font-size: 0.9rem; }

.books-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr)); 
  gap: 16px; 
  padding: 20px 0;
}
.book-card { background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06); border: 1px solid #eef0f2; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.22s, box-shadow 0.22s; }
.book-card:hover { transform: translateY(-6px); box-shadow: 0 12px 20px rgba(0, 0, 0, 0.12); }

.image-wrapper {
  position: relative;
  width: 100%;
  height: 240px; 
  background-color: #f4f5f7; 
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.book-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain; 
  padding: 8px; 
}
.book-status { position: absolute; top: 12px; left: 12px; font-size: 0.75rem; font-weight: bold; padding: 5px 10px; border-radius: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }
.book-status.available { background-color: #e8f5e9; color: #2e7d32; }
.book-status.borrowed { background-color: #ffebee; color: #c62828; }

.card-body { padding: 15px; display: flex; flex-direction: column; flex-grow: 1; }
.book-title { margin: 0 0 5px 0; font-size: 1.15rem; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.book-author { margin: 0 0 12px 0; color: #7f8c8d; font-size: 0.9rem; }
.meta-tags { display: flex; flex-direction: wrap; gap: 8px; margin-top: auto; }
.book-city, .book-condition { font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; font-weight: 500; }
.book-city { background: #eef2f7; color: #34495e; }

.book-condition { background: #f1f3f5; color: #495057; }
.book-condition.nouă { background: #e3f2fd; color: #0d47a1; }
.book-condition.bună { background: #e8f5e9; color: #1b5e20; }
.book-condition.uzată { background: #fff3e0; color: #e65100; }

.card-footer-buttons { padding: 15px; background: #fafbfc; border-top: 1px solid #f0f2f5; display: flex; flex-direction: column; gap: 10px; }
.owner-rating-box { display: flex; justify-content: space-between; align-items: center; }
.owner-rating-box small { font-size: 0.7rem; color: #95a5a6; text-transform: uppercase; letter-spacing: 0.5px; }

.actions-wrapper { display: flex; gap: 8px; width: 100%; }
.profile-btn, .request-btn { flex: 1; padding: 8px 10px; font-size: 0.8rem; font-weight: bold; border-radius: 6px; cursor: pointer; text-align: center; border: none; transition: all 0.2s; }

.profile-btn { background: #3498db; color: white; }
.profile-btn:hover { background: #2980b9; }

.request-btn { background: #42b983; color: white; }
.request-btn:hover { background: #3aa876; }
.no-results { text-align: center; margin-top: 30px; color: #780606; font-weight: bold; }
.own-book-message {
  width: 95%;
  text-align: center;
  padding: 8px;
  background-color: #ebf5fe;
  color: #1e88e5;
  font-size: 0.85rem;
  font-weight: bold;
  border-radius: 10px;
  border:2px dashed #2196f3;
}

@media (max-width: 1200px) {
  .books-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr)); 
  }
}
@media (max-width: 768px) {
  .books-grid {
    grid-template-columns: repeat(1, minmax(0, 1fr)); 
  }
}
</style>