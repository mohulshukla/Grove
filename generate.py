import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_random_vectors(num_vectors, dimension):
    """
    Generates a specified number of random 3-dimensional vectors.
    
    Args:
        num_vectors (int): The number of vectors to generate.
    
    Returns:
        list: A list of tuples, each containing an ID and a 3-dimensional random vector.
    """
    vectors = []
    for i in range(num_vectors):
        vector_id = f'vec_{i + 1}'  # Unique ID for each vector
        random_vector = [random.uniform(0, 10) for _ in range(dimension)]  # Random float values between 0 and 10
        vectors.append((vector_id, random_vector))
    
    return vectors

def chunker(seq, batch_size):
    """
    Splits data into chunks for batch processing.
    
    Args:
        seq (list): The data to be chunked.
        batch_size (int): The number of items in each chunk.
    
    Yields:
        list: Chunks of data.
    """
    return (seq[pos:pos + batch_size] for pos in range(0, len(seq), batch_size))

def upsert_batch(index, batch):
    """
    Upserts a single batch of vectors to the Pinecone index.
    
    Args:
        index: The Pinecone index instance.
        batch (list): A batch of vectors to be upserted.
    """
    return index.upsert(vectors=batch)

def upsert_large_dataset(index, data, batch_size=1000):
    """
    Upserts a large dataset to the Pinecone index in batches.
    
    Args:
        index: The Pinecone index instance.
        data (list): The list of vectors to be upserted.
        batch_size (int, optional): The number of vectors per batch. Default is 1000.
    """
    with ThreadPoolExecutor() as executor:
        futures = []
        for chunk in chunker(data, batch_size):
            future = executor.submit(upsert_batch, index, chunk)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred during upsert: {e}")

def query_similar_vectors(index, query_vector, top_k=5):
    """
    Queries the index to find similar vectors to a given query vector.
    
    Args:
        index: The Pinecone index instance.
        query_vector (list): The vector to use for querying.
        top_k (int, optional): Number of similar vectors to return. Default is 5.
    
    Returns:
        The query results with the top-k most similar vectors.
    """
    try:
        return index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    except Exception as e:
        print(f"An error occurred during query: {e}")
        return None