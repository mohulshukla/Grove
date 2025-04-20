# Grove

Intentional scrolling. Seamlessly swipe through categories and curate your brainrot feed to your desires. You are in control.

The user can access an application where:
1. An initial random video is displayed.
2. Scrolling down shows a video similar to the previous one.
3. Scrolling left or right shows a random video from another category. Then scrolling down again shows a video similar to the current video.

Video embeddings are created using the ViViT vision transformer and stored on a Pinecone vector database. These embeddings are used to find similar videos.
