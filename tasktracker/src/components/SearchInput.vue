<template>
    <div class="search-box-container">
        <div class="search-box">
            <input
                type="text"
                class="search-input"
                :placeholder="placeholder"
                :value="modelValue"
                @input="handleInput"
            >
            <i class="bi bi-search"></i>
        </div>
    </div>
</template>

<script>
import {debounce} from 'lodash';

export default {
    name: 'SearchInput',
    props: {
        placeholder: {
            type: String,
            default: 'Поиск...'
        },
        modelValue: {
            type: String,
            default: ''
        },
        debounceTime: {
            type: Number,
            default: 300
        }
    },
    emits: ['update:modelValue', 'search'],
    methods: {
        handleInput(event) {
            this.$emit('update:modelValue', event.target.value);
            this.debouncedSearch();
        },
        emitSearch() {
            this.$emit('search', this.modelValue);
        }
    },
    created() {
        this.debouncedSearch = debounce(this.emitSearch, this.debounceTime);
    },
    beforeUnmount() {
        this.debouncedSearch.cancel();
    }
}
</script>

<style scoped>

.search-box {
    position: relative;
    width: 300px;
}

.search-box input {
    width: 100%;
    padding: 8px 12px 8px 32px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.search-box .bi {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
}

.search-input:focus {
    outline: none;
    border-color: #6498F1;
    box-shadow: 0 0 0 2px rgba(100, 152, 241, 0.2);
}

.search-box-container {
    position: absolute;
    left: 35%;
    transform: translateX(-50%);
}
</style>